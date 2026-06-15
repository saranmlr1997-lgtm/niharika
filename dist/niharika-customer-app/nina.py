import os

from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

client = None


KNOWLEDGE_BASE = {
    "wholesale_resources": [
        {
            "source": "Niharika wholesale intake",
            "topic": "Buyer Requirement Basics",
            "insight": "A useful wholesale enquiry should include category, quantity, budget range, delivery city, and purchase timeline.",
        },
        {
            "source": "Niharika category guide",
            "topic": "Product Categories",
            "insight": "Niharika focuses on Sarees, Kurtis, and Crop tops for wholesale buyer conversations.",
        },
    ],
    "business_advice": [
        {
            "name": "Niharika sales team",
            "expertise": "Wholesale follow-up",
            "advice": "Ask for business name, Instagram handle, phone or WhatsApp number, product category, and pieces required before preparing a quote.",
        },
        {
            "name": "Niharika buyer desk",
            "expertise": "Order qualification",
            "advice": "For serious wholesale leads, confirm whether the buyer is a shop, boutique, reseller, or business customer.",
        },
    ],
}


def build_enriched_prompt(user_message, user_type):
    """Inject Niharika wholesale guidance into the model context."""
    context = "Here is verified Niharika wholesale guidance:\n"

    if user_type == "wholesale buyer":
        for item in KNOWLEDGE_BASE["wholesale_resources"]:
            context += f"- From {item['source']}: {item['insight']}\n"
    else:
        for mentor in KNOWLEDGE_BASE["business_advice"]:
            context += (
                f"- Advice from {mentor['name']} "
                f"({mentor['expertise']}): {mentor['advice']}\n"
            )

    return (
        f"{context}\nUser's Request: {user_message}\n"
        "Please provide a tailored response using the context above if relevant."
    )


def get_system_instruction(user_type):
    base_rules = (
        "Keep your response under 3 sentences. Do not use any markdown formatting or lists. "
        "Reference Niharika wholesale categories naturally when giving advice. "
        "Always end with a targeted follow-up question."
    )
    if user_type == "wholesale buyer":
        return f"You are Nina, the Niharika wholesale chatbot for buyer requirements. {base_rules}"

    return f"You are Nina, the Niharika business assistant for wholesale enquiries. {base_rules}"


def get_client():
    global client
    if client is None:
        from google import genai

        client = genai.Client()
    return client


def fallback_chat_reply(user_message):
    lower = user_message.lower()
    if any(word in lower for word in ["saree", "sarees"]):
        reply = "For Niharika sarees, please share fabric preference, quantity, budget per piece, and delivery city so the team can prepare a useful wholesale quote."
        next_question = "How many sarees do you need and where should they be delivered?"
    elif any(word in lower for word in ["kurti", "kurtis"]):
        reply = "For Niharika kurtis, Nina should capture quantity, size mix, target price, quality level, and delivery timeline before sales follow-up."
        next_question = "What quantity and budget range should I note for the kurti enquiry?"
    elif any(word in lower for word in ["crop", "top", "tops"]):
        reply = "For crop tops, please share style, size mix, color preference, quantity, and whether this is for resale or boutique stock."
        next_question = "What size mix and delivery city should Niharika use for the quote?"
    elif any(word in lower for word in ["price", "budget", "quote", "cost"]):
        reply = "Niharika can quote better when Nina has category, quantity, budget range, delivery city, and purchase timeline."
        next_question = "Which category and quantity should I prepare the quote around?"
    else:
        reply = "I am Nina for Niharika. I can collect wholesale requirements for Sarees, Kurtis, and Crop tops, then guide the next buying step."
        next_question = "What product category, quantity, budget, and delivery city should I note?"

    return f"{reply} {next_question}"


@app.get("/")
def home():
    return app.send_static_file("nina.html")


@app.get("/api/health")
def health():
    return jsonify({"app": "Nina", "status": "ok"})


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    user_type = data.get("user_type", "wholesale buyer")

    if not user_message:
        return jsonify({"error": "Message is required."}), 400

    if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        return jsonify({"reply": fallback_chat_reply(user_message), "provider": "nina-local-fallback"})

    enriched_contents = build_enriched_prompt(user_message, user_type)

    try:
        from google.genai import types

        response = get_client().models.generate_content(
            model=os.environ.get("NINA_GEMINI_MODEL", "gemini-2.5-flash"),
            contents=enriched_contents,
            config=types.GenerateContentConfig(
                system_instruction=get_system_instruction(user_type),
                temperature=0.5,
            ),
        )
        return jsonify({"reply": response.text})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(
        debug=os.environ.get("NINA_DEBUG") == "1",
        port=int(os.environ.get("NINA_PORT", "5000")),
        use_reloader=False,
    )

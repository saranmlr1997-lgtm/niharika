import os

from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

client = None


KNOWLEDGE_BASE = {
    "fashiontech_resources": [
        {
            "source": "Niharika fashiontech intake",
            "topic": "Buyer Requirement Basics",
            "insight": "A strong fashion enquiry includes product category, occasion, fabric preference, size mix, quantity, budget, delivery city, and purchase timeline.",
        },
        {
            "source": "Niharika style guide",
            "topic": "Product Categories",
            "insight": "Niharika focuses on Sarees, Kurtis, and Crop tops, with styling guidance for festive, office, casual, boutique, and resale needs.",
        },
        {
            "source": "Niharika merchandising guide",
            "topic": "Boutique Inventory",
            "insight": "Boutiques should clarify target customer, size curve, preferred colors, margin goal, repeat-stock potential, and whether the collection is trend-led or evergreen.",
        },
    ],
    "business_advice": [
        {
            "name": "Niharika fashion desk",
            "expertise": "Fashiontech merchandising",
            "advice": "Ask for business name, Instagram handle, customer segment, product category, size mix, price band, margin target, and pieces required before preparing a quote.",
        },
        {
            "name": "Niharika buyer desk",
            "expertise": "Order qualification",
            "advice": "For serious fashion leads, confirm whether the buyer is a shop, boutique, reseller, creator, stylist, or direct customer.",
        },
        {
            "name": "Niharika styling desk",
            "expertise": "Style matching",
            "advice": "Match recommendations to occasion, climate, age group, fabric comfort, color preference, and whether the buyer wants fast-moving basics or standout statement pieces.",
        },
    ],
}


def build_enriched_prompt(user_message, user_type):
    """Inject Niharika fashiontech guidance into the model context."""
    context = "Here is verified Niharika fashiontech guidance:\n"

    if user_type in {"fashion buyer", "wholesale buyer", "customer"}:
        for item in KNOWLEDGE_BASE["fashiontech_resources"]:
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
        "Behave like a fashiontech chatbot: combine style advice, merchandising logic, and buying qualification. "
        "Reference Niharika categories naturally: Sarees, Kurtis, and Crop tops. "
        "Ask for missing fashion signals such as occasion, fabric, size mix, budget, quantity, margin, or delivery city. "
        "Always end with one targeted follow-up question."
    )
    if user_type in {"fashion buyer", "wholesale buyer", "customer"}:
        return f"You are Nina, the Niharika fashiontech chatbot for buyer styling and wholesale requirements. {base_rules}"

    return f"You are Nina, the Niharika fashiontech business assistant for boutique, reseller, and inventory decisions. {base_rules}"


def get_client():
    global client
    if client is None:
        from google import genai

        client = genai.Client()
    return client


def fallback_chat_reply(user_message):
    lower = user_message.lower()
    if any(word in lower for word in ["saree", "sarees"]):
        reply = "For Niharika sarees, Nina can help choose between festive, daily wear, boutique resale, or premium looks using fabric, color, budget, and occasion."
        next_question = "What occasion, fabric preference, quantity, and delivery city should I match for the saree requirement?"
    elif any(word in lower for word in ["kurti", "kurtis", "kurta"]):
        reply = "For Niharika kurtis, Nina can plan a size mix, color story, price band, and margin-friendly assortment for boutique or reseller stock."
        next_question = "What size range, quantity, and target selling price should I use for the kurti recommendation?"
    elif any(word in lower for word in ["crop", "top", "tops"]):
        reply = "For crop tops, Nina can match trend, color, size mix, and customer segment so the stock feels current and sellable."
        next_question = "Is this for college wear, party wear, boutique resale, or casual daily stock?"
    elif any(word in lower for word in ["style", "trend", "occasion", "festival", "wedding", "office", "college"]):
        reply = "Nina can style-match Niharika pieces by occasion, age group, climate, fabric comfort, and budget before turning it into a buying shortlist."
        next_question = "Which occasion and customer age group should I style for?"
    elif any(word in lower for word in ["price", "budget", "quote", "cost", "margin", "profit"]):
        reply = "For fashion buying, Nina needs target cost, expected selling price, quantity, and customer segment to judge margin and stock fit."
        next_question = "What is your target cost per piece and expected selling price?"
    else:
        reply = "I am Nina, the Niharika fashiontech assistant. I can help with styling, product discovery, boutique buying, wholesale quantity planning, and resale-ready fashion recommendations."
        next_question = "Are you looking for Sarees, Kurtis, Crop tops, or a full boutique assortment?"

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

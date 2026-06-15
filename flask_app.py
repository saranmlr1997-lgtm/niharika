import json
import mimetypes
import os
from urllib.parse import unquote

from flask import Flask, Response, jsonify, request, send_file

from saas_store import SaaSStore
from app import ADMIN_HTML, COURSERA_BLOG_FEED, CUSTOMER_LOGIN_HTML, EDTECH_APIS, NIHARIKA_ADMIN_TOKEN, NIHARIKA_INSTAGRAM_URL
from app import (
    SIGNUP_HTML,
    SITE_NAME,
    SITEMAP_XML,
    SURVEY_HTML,
    TOPMATE_MENTORS,
    admin_update_business,
    catalog_images_dir,
    connect_shopify_store,
    connected_nina_requirement_reply,
    create_business,
    extract_license_key,
    free_retail_wholesale_rank,
    free_requirement_payload,
    get_business_by_license_key,
    get_coursera_posts,
    get_license_record,
    is_license_active,
    list_loom_media,
    list_short_film_media,
    load_catalog,
    load_leads,
    load_survey_responses,
    media_dir,
    niharika_api_chat,
    payment_instruction_for_business,
    payment_link_for_business,
    payment_whatsapp_url,
    public_business_record,
    public_customer_record,
    public_license_record,
    rank_recommendations,
    save_lead,
    save_survey_response,
    sign_in_business,
    sign_in_customer_with_google,
    static_home_html,
    survey_csv_content,
    update_lead_status,
)
from datetime import datetime, timezone


app = Flask(__name__, static_folder=".", static_url_path="")
SAAS_STORE = SaaSStore(os.path.dirname(__file__))


def allowed_origin():
    origin = request.headers.get("Origin", "")
    allowed_origins = {
        "http://127.0.0.1:8080",
        "http://localhost:8080",
        "https://www.niharika.com",
        "https://nina.niharika.com",
    }
    return origin if origin in allowed_origins else ""


@app.after_request
def add_security_headers(response):
    origin = allowed_origin()
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Niharika-License"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://accounts.google.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https://images.unsplash.com https://www.instagram.com; "
        "media-src 'self'; "
        "connect-src 'self'; "
        "frame-src https://accounts.google.com; "
        "base-uri 'self'; "
        "form-action 'self' mailto:"
    )
    if request.path.startswith("/admin") or request.path.startswith("/api/admin") or request.path.startswith("/survey-responses.csv"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def home():
    return Response(static_home_html(), mimetype="text/html")


@app.route("/signup", methods=["GET"])
def signup_page():
    return Response(SIGNUP_HTML, mimetype="text/html")


@app.route("/admin", methods=["GET"])
def admin_page():
    return Response(ADMIN_HTML, mimetype="text/html")


@app.route("/survey", methods=["GET"])
def survey_page():
    return Response(SURVEY_HTML, mimetype="text/html")


@app.route("/customer-login", methods=["GET"])
def customer_login_page():
    return Response(CUSTOMER_LOGIN_HTML, mimetype="text/html")


@app.route("/robots.txt", methods=["GET"])
def robots():
    return Response("User-agent: *\nAllow: /\nSitemap: https://www.niharika.com/sitemap.xml\n", mimetype="text/plain")


@app.route("/sitemap.xml", methods=["GET"])
def sitemap():
    return Response(SITEMAP_XML, mimetype="application/xml")


@app.route("/api/coursera-blogs", methods=["GET"])
def coursera_blogs():
    return jsonify(
        {
            "source": COURSERA_BLOG_FEED,
            "updated": datetime.now(timezone.utc).isoformat(),
            "posts": get_coursera_posts(),
        }
    )


@app.route("/api/edtech-integrations", methods=["GET"])
def edtech_integrations():
    return jsonify({"updated": datetime.now(timezone.utc).isoformat(), "integrations": EDTECH_APIS})


@app.route("/api/topmate-mentors", methods=["GET"])
def topmate_mentors():
    return jsonify(
        {
            "updated": datetime.now(timezone.utc).isoformat(),
            "filter": "public profiles with 7+ years experience signals",
            "mentors": TOPMATE_MENTORS,
        }
    )


@app.route("/api/catalog", methods=["GET"])
def catalog():
    return jsonify({"items": load_catalog()})


@app.route("/api/loom-media", methods=["GET"])
def loom_media():
    return jsonify({"items": list_loom_media()})


@app.route("/api/short-film-media", methods=["GET"])
def short_film_media():
    return jsonify({"items": list_short_film_media()})


@app.route("/api/free/catalog", methods=["GET"])
def free_catalog():
    return jsonify(
        {
            "free_api": True,
            "usage": "Use this public catalogue API for wholesale or retail discovery. No license required.",
            "items": load_catalog(),
        }
    )


@app.route("/catalog-images/<path:filename>", methods=["GET"])
def catalog_image(filename):
    image_path = os.path.abspath(os.path.join(catalog_images_dir(), os.path.basename(filename)))
    image_root = os.path.abspath(catalog_images_dir())
    if not image_path.startswith(image_root) or not os.path.isfile(image_path):
        return jsonify({"error": "Image not found"}), 404
    return send_file(image_path, mimetype=mimetypes.guess_type(image_path)[0] or "application/octet-stream")


@app.route("/media/<path:relative_path>", methods=["GET"])
def media_file(relative_path):
    normalized = os.path.normpath(unquote(relative_path).replace("\\", "/"))
    if normalized.startswith("..") or os.path.isabs(normalized):
        return jsonify({"error": "Media not found"}), 404
    media_path = os.path.abspath(os.path.join(media_dir(), normalized))
    media_root = os.path.abspath(media_dir())
    if not media_path.startswith(media_root) or not os.path.isfile(media_path):
        return jsonify({"error": "Media not found"}), 404
    return send_file(media_path, mimetype=mimetypes.guess_type(media_path)[0] or "application/octet-stream")


@app.route("/survey-responses.csv", methods=["GET"])
def survey_csv():
    token = request.args.get("token", "")
    if token != NIHARIKA_ADMIN_TOKEN:
        return jsonify({"error": "Invalid admin token."}), 401
    return Response(survey_csv_content(), mimetype="text/csv")


def payload():
    return request.get_json(silent=True) or {}


@app.route("/api/business/signup", methods=["POST"])
def business_signup():
    business, error = create_business(payload())
    if error:
        return jsonify({"error": error}), 400
    return (
        jsonify(
            {
                "business": public_business_record(business),
                "payment_link": payment_link_for_business(business),
                "payment_whatsapp_url": payment_whatsapp_url(business),
                "payment_instruction": payment_instruction_for_business(),
                "message": "First month is free. Connect Shopify, set up payment for later billing, and complete Instagram verification to activate API access.",
            }
        ),
        201,
    )


@app.route("/api/auth/google", methods=["POST"])
def auth_google():
    customer, error = sign_in_customer_with_google(payload())
    if error:
        return jsonify({"error": error}), 401
    return jsonify({"customer": public_customer_record(customer)})


@app.route("/api/business/signin", methods=["POST"])
def business_signin():
    business = sign_in_business(payload())
    if not business:
        return jsonify({"error": "Invalid email or password."}), 401
    return jsonify(
        {
            "business": public_business_record(business),
            "payment_link": payment_link_for_business(business),
            "payment_whatsapp_url": payment_whatsapp_url(business),
            "payment_instruction": payment_instruction_for_business(),
        }
    )


@app.route("/api/shopify/connect", methods=["POST"])
def shopify_connect():
    business, error = connect_shopify_store(payload())
    if error:
        return jsonify({"error": error}), 400
    return jsonify(
        {
            "business": public_business_record(business),
            "message": "Shopify store connected. Recommendations can now return Shopify product/search URLs.",
        }
    )


@app.route("/api/admin/business/update", methods=["POST"])
def admin_business_update():
    business, error = admin_update_business(payload())
    if error:
        return jsonify({"error": error}), 401
    return jsonify({"business": public_business_record(business)})


@app.route("/api/admin/leads", methods=["POST"])
def admin_leads():
    body = payload()
    if body.get("admin_token") != NIHARIKA_ADMIN_TOKEN:
        return jsonify({"error": "Invalid admin token."}), 401
    return jsonify({"leads": load_leads()})


@app.route("/api/admin/lead/update", methods=["POST"])
def admin_lead_update():
    body = payload()
    if body.get("admin_token") != NIHARIKA_ADMIN_TOKEN:
        return jsonify({"error": "Invalid admin token."}), 401
    lead, error = update_lead_status(body)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"lead": lead})


@app.route("/api/admin/surveys", methods=["POST"])
def admin_surveys():
    body = payload()
    if body.get("admin_token") != NIHARIKA_ADMIN_TOKEN:
        return jsonify({"error": "Invalid admin token."}), 401
    return jsonify({"responses": load_survey_responses()})


@app.route("/api/admin/tenants", methods=["POST"])
def admin_tenants():
    body = payload()
    if body.get("admin_token") != NIHARIKA_ADMIN_TOKEN:
        return jsonify({"error": "Invalid admin token."}), 401
    return jsonify({"tenants": SAAS_STORE.tenant_summary()})


@app.route("/api/license/verify", methods=["POST"])
def license_verify():
    body = payload()
    license_key = extract_license_key(request.headers, body)
    record = get_license_record(license_key)
    active = is_license_active(record)
    return (
        jsonify({"valid": active, "license": public_license_record(record) if active else None}),
        200 if active else 401,
    )


@app.route("/api/free/recommend", methods=["POST"])
def free_recommend():
    body = payload()
    recommendations = free_retail_wholesale_rank(body)
    return jsonify(
        {
            "free_api": True,
            "request_type": body.get("request_type") or body.get("buyer_type") or "wholesale",
            "recommendations": recommendations,
            "best_pick": recommendations[0] if recommendations else None,
            "contact": {
                "email": "sivashankarimurugesan@niharika.com",
                "instagram": NIHARIKA_INSTAGRAM_URL,
            },
        }
    )


@app.route("/api/free/requirements", methods=["POST"])
def free_requirements():
    return jsonify(free_requirement_payload(payload())), 201


@app.route("/api/free/chat", methods=["POST"])
def free_chat():
    return jsonify(niharika_api_chat(payload()))


@app.route("/api/free/survey", methods=["POST"])
def free_survey():
    body = payload()
    response, error = save_survey_response({**body, "source": body.get("source") or "niharika-free-api"})
    if error:
        return jsonify(error), 400
    return jsonify({"free_api": True, "response": response}), 201


@app.route("/api/recommend", methods=["POST"])
def recommend():
    body = payload()
    license_key = extract_license_key(request.headers, body)
    record = get_license_record(license_key)
    if not is_license_active(record):
        return jsonify({"error": "Active Niharika business license required."}), 401
    business = get_business_by_license_key(license_key)
    if business and not body.get("shopify_store_domain"):
        body["shopify_store_domain"] = business.get("shopify_store_domain", "")
    recommendations = rank_recommendations(body)
    return jsonify(
        {
            "license": public_license_record(record),
            "shopify_store_domain": body.get("shopify_store_domain", ""),
            "recommendations": recommendations,
            "best_pick": recommendations[0] if recommendations else None,
        }
    )


@app.route("/api/nina/requirements", methods=["POST"])
def nina_requirements():
    body = payload()
    result = connected_nina_requirement_reply(body)
    result["lead"] = save_lead(body, result)
    return jsonify(result)


@app.route("/api/survey/submit", methods=["POST"])
def survey_submit():
    response, error = save_survey_response(payload())
    if error:
        return jsonify(error), 400
    return jsonify({"response": response}), 201


@app.route("/<path:path>", methods=["OPTIONS"])
@app.route("/", methods=["OPTIONS"])
def options_handler(path=""):
    return Response(status=204)


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    print(f"{SITE_NAME} Flask app is running at http://{host}:{port}")
    app.run(host=host, port=port, debug=False)

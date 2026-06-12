# Niharika Free API

Niharika exposes a free public API for wholesale and retail discovery.

Use it for:

- Catalogue display
- Wholesale buyer enquiry capture
- Retail buyer enquiry capture
- Gemini-style AI chat integration
- Simple recommendation ranking
- Nina requirement intake

Admin data and exports still require the secure admin token.

## Free Catalogue API

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/free/catalog
```

Response:

```json
{
  "free_api": true,
  "items": []
}
```

## Free Recommendation API

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/free/recommend `
  -Method POST `
  -ContentType "application/json" `
  -Body '{
    "request_type": "wholesale",
    "product_category": "Sarees",
    "quantity": "100",
    "budget": "mid range",
    "delivery_city": "Bangalore"
  }'
```

## Free Requirement API

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/free/requirements `
  -Method POST `
  -ContentType "application/json" `
  -Body '{
    "name": "Demo Buyer",
    "phone": "9999999999",
    "buyer_type": "retail",
    "message": "Need 2 kurtis for personal use in Bangalore"
  }'
```

This creates a lead for admin follow-up.

## Free Gemini-Style Chat API

Use this endpoint when another retail or wholesale website wants to talk to Nina like an AI API.

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/free/chat `
  -Method POST `
  -ContentType "application/json" `
  -Body '{
    "message": "Need 80 sarees for my boutique in Bangalore under mid range budget",
    "buyer_type": "wholesale",
    "product_category": "Sarees",
    "quantity": "80",
    "delivery_city": "Bangalore"
  }'
```

Response shape:

```json
{
  "free_api": true,
  "provider": "google-gemini",
  "model": "gemini-2.5-flash",
  "reply": "Nina response text",
  "requirements": {},
  "next_question": "What delivery timeline should I note?",
  "recommendations": [],
  "best_pick": null
}
```

If `GOOGLE_API_KEY` is not configured, this endpoint still works with Niharika's built-in fallback logic and returns `ai_status: fallback_no_google_api_key`.

## Free Survey API

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/free/survey `
  -Method POST `
  -ContentType "application/json" `
  -Body '{
    "wholesale_order_no": "WEB-001",
    "name": "Demo Buyer",
    "phone": "9999999999",
    "business_name": "Demo Store",
    "product_category": "Sarees",
    "pieces_required": "50",
    "delivery_city": "Bangalore",
    "requirements": "Need premium sarees for resale"
  }'
```

This saves to local survey JSON/CSV and Google Sheets when connected.

## Optional Paid/Private API

Niharika still supports private license-gated APIs for paid business integrations:

- `/api/license/verify`
- `/api/recommend`

Use `X-Niharika-License` or `Authorization: Bearer ...` for paid/private access.

# Niharika Shopify Integration

Niharika can now work as a recommendation layer in front of a Shopify store for Rs. 500/month.

## What Customers Get

- Business sign-up and monthly license key
- Instagram business verification status
- Shopify store connection
- Recommendation API that returns Shopify product or search URLs
- Survey/lead capture for wholesale requirements

## Shopify Notes

Shopify's Admin API requires an access token sent as `X-Shopify-Access-Token`. Shopify's current docs say the REST Admin API is legacy for new public apps, and new public apps should use GraphQL Admin API. This lightweight integration is designed for custom/private store setup and product link routing first.

## Connect A Shopify Store

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/shopify/connect `
  -Method POST `
  -ContentType "application/json" `
  -Body '{
    "email": "merchant@example.com",
    "license_key": "PW-CUSTOMER-KEY",
    "shopify_store_domain": "yourstore.myshopify.com"
  }'
```

Optional local-only Admin API token:

```json
{
  "shopify_admin_access_token": "shpat_xxx"
}
```

Do not share Shopify Admin tokens publicly.

## Recommendation API With Shopify Links

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/recommend `
  -Method POST `
  -ContentType "application/json" `
  -Body '{
    "license_key": "PW-CUSTOMER-KEY",
    "options": [
      {
        "name": "Premium Saree",
        "product_handle": "premium-saree",
        "quality": 9,
        "price_fit": 8,
        "outcome_fit": 9,
        "support": 8,
        "next_step": "Open Shopify product page."
      }
    ]
  }'
```

The API returns:

- recommendation score
- reasons
- best pick
- `shopify_url`

If `product_handle` is missing, Niharika returns a Shopify search URL for the option name.

## Pricing

Starter Shopify plan:

Rs. 500/month per business.

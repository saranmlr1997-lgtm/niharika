# Niharika Wholesale

Niharika Wholesale is a lightweight B2B wholesale website with a catalogue, buyer survey, admin dashboard, and Nina chatbot.

## Main URLs

- Niharika Wholesale: `http://127.0.0.1:8080/`
- Niharika Admin: `http://127.0.0.1:8080/admin`
- Niharika Survey: `http://127.0.0.1:8080/survey`
- Nina Chatbot: `http://127.0.0.1:5000/`

## Run Niharika

Use the bundled Python runtime if normal `python` is not on PATH:

```powershell
cd "C:\Users\saran\niharika"
$env:HOST = "0.0.0.0"
$env:PORT = "8080"
& "C:\Users\saran\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" app.py
```

## Run Niharika As Flask

The repo now includes a Flask application entrypoint for a more standard API/app deployment path:

```powershell
cd "C:\Users\saran\niharika"
$env:HOST = "0.0.0.0"
$env:PORT = "8080"
& "C:\Users\saran\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" flask_app.py
```

This keeps the existing routes and business logic, but serves them through Flask so the project is easier to evolve toward a SaaS-style deployment.

## SaaS Foundation

The project now includes an initial multi-tenant storage layer:

- `saas_store.py` stores businesses and leads in SQLite
- each business gets a `tenant_slug`
- leads are stored with tenant-aware fields
- the Flask app exposes `POST /api/admin/tenants` for a simple tenant summary view

This is a foundation step toward a real SaaS app. It keeps the current API shape while moving the project away from flat JSON-only storage.

## Run Nina

Nina is a Flask chatbot app. Gemini is optional and requires `GOOGLE_API_KEY`.

```powershell
cd "C:\Users\saran\niharika"
$env:GOOGLE_API_KEY = "your-gemini-api-key"
& "C:\Users\saran\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" nina.py
```

## Secrets

Do not commit real secrets or customer data. Put local values in:

`C:\Users\saran\niharika\niharika-secrets.ps1`

Use `niharika-secrets-template.ps1` as the template.

## Public Access

Temporary Cloudflare links are generated with `cloudflared`. Permanent DNS for `www.niharika.com` must point to the named Cloudflare tunnel target documented in `NIHARIKA_DNS_SETTINGS.txt`.

## Deploy This Repo To The Live Windows App

This repo is the clean GitHub source. The currently live app still runs from:

`C:\Users\saran\niharika`

To copy the repo contents into the live folder and restart the local services plus Cloudflare tunnel, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy-live-update.ps1
```

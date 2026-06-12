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

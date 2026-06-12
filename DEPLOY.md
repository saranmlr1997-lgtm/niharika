# Publish Niharika Wholesale

Niharika runs as a local Python app and is exposed publicly through Cloudflare Tunnel.

## Local Services

- Niharika Wholesale: `http://127.0.0.1:8080/`
- Admin: `http://127.0.0.1:8080/admin`
- Survey: `http://127.0.0.1:8080/survey`
- Nina: `http://127.0.0.1:5000/`

## Run Locally

```powershell
cd "C:\Users\saran\niharika"
$env:HOST = "0.0.0.0"
$env:PORT = "8080"
& "C:\Users\saran\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" app.py
```

In another process:

```powershell
cd "C:\Users\saran\niharika"
& "C:\Users\saran\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" nina.py
```

## Permanent Cloudflare Tunnel

Tunnel name:

`niharika-wholesale`

Tunnel target:

`582142fb-5ff8-4520-8254-f24acdbad701.cfargotunnel.com`

Config path:

`C:\Users\saran\.cloudflared\config.yml`

Expected ingress:

- `www.niharika.com` -> `http://127.0.0.1:8080`
- `nina.niharika.com` -> `http://127.0.0.1:5000`

## DNS Records

In the domain DNS provider, delete old `www` A/AAAA records and add:

```text
Type: CNAME
Name: www
Target: 582142fb-5ff8-4520-8254-f24acdbad701.cfargotunnel.com
```

Optional Nina subdomain:

```text
Type: CNAME
Name: nina
Target: 582142fb-5ff8-4520-8254-f24acdbad701.cfargotunnel.com
```

## Secrets

Do not commit real secrets. Use:

`C:\Users\saran\niharika\niharika-secrets.ps1`

Template:

`niharika-secrets-template.ps1`

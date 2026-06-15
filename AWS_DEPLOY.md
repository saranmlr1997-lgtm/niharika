# AWS Deploy Guide

This project is ready for a first AWS deployment.

## Recommended first setup

Use one small EC2 instance for the web app and one small EC2 instance for Nina, or run both services on a single EC2 instance with `nginx` in front.

Why this is the best first move:
- the app still stores business data in local JSON and SQLite files
- a single host keeps that storage simple and predictable
- you can move to RDS/S3 later without blocking launch

## Current service layout

- Main site and API: `flask_app.py`
- Nina chatbot API: `nina.py`
- Main app default port: `8080`
- Nina default port: `5000`

The main app calls Nina through `NINA_CHAT_URL`, so in AWS you should set that environment variable to the Nina service URL.

Example:

```bash
NINA_CHAT_URL=http://127.0.0.1:5000/api/chat
```

If Nina runs on a second EC2 machine or a private App Runner service, use that internal URL instead.

## Option 1: EC2 + nginx

This is the most practical launch option for this codebase.

### 1. Create the server

- Launch Ubuntu 24.04 LTS
- Use `t3.small` or `t3.medium`
- Open ports `80` and `443`
- Open `22` only for your admin IP

### 2. Install packages

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx git
```

### 3. Clone the repo

```bash
git clone https://github.com/saranmlr1997-lgtm/niharika.git
cd niharika
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Environment variables

Create a file such as `/etc/niharika.env`:

```bash
HOST=0.0.0.0
PORT=8080
NINA_PORT=5000
NINA_CHAT_URL=http://127.0.0.1:5000/api/chat
GOOGLE_API_KEY=your-gemini-key
NIHARIKA_ADMIN_TOKEN=replace-this
NIHARIKA_UPI_ID=sivas21093@okicici
NIHARIKA_WHATSAPP_NUMBER=918149869054
GOOGLE_CLIENT_ID=your-google-client-id
```

### 5. Start the web app with Gunicorn

```bash
cd ~/niharika
source .venv/bin/activate
set -a
source /etc/niharika.env
set +a
gunicorn -c gunicorn.conf.py flask_app:app
```

### 6. Start Nina with Gunicorn

In a second shell or service:

```bash
cd ~/niharika
source .venv/bin/activate
set -a
source /etc/niharika.env
set +a
gunicorn -c gunicorn_nina.conf.py nina:app
```

### 7. nginx reverse proxy

Point public traffic to Gunicorn on port `8080`.

Basic idea:
- `server_name niharika.com www.niharika.com`
- proxy `/` to `127.0.0.1:8080`
- keep Nina private unless you explicitly want `nina.niharika.com`

If you also want Nina public:
- map `nina.niharika.com` to `127.0.0.1:5000`

### 8. HTTPS

Use either:
- AWS Certificate Manager with an Application Load Balancer, or
- `certbot` with nginx on EC2

If you want the simplest first version on one box:
- use `nginx` + `certbot`

## Option 2: AWS App Runner

Use this when you want managed deployment and easier HTTPS.

Important:
- this app is not yet a perfect autoscaling SaaS because it still uses local file storage
- App Runner works best after moving business data to RDS or another shared database

### Service split

Create two services:

1. `niharika-web`
- source: GitHub repo
- Dockerfile: `Dockerfile.web`
- port: `8080`
- env var: `NINA_CHAT_URL=http://<private-nina-url>/api/chat`

2. `niharika-nina`
- source: same repo
- Dockerfile: `Dockerfile.nina`
- port: `5000`

### App Runner notes

- `niharika-web` can be public
- `niharika-nina` should preferably stay private
- if private App Runner networking is inconvenient, EC2 is the easier first deployment

## Domain setup on AWS

If you move DNS into Route 53:
- create hosted zone for `niharika.com`
- point `A/AAAA` alias records to the load balancer or App Runner custom domain

If DNS stays outside AWS:
- point `www` and root records to the AWS endpoint
- remove old IONOS records first

## Storage warning

Today the app stores business and lead data in:
- `businesses.json`
- `leads.json`
- `licenses.json`
- `survey_responses.json`
- `niharika_saas.db`

That is acceptable for:
- one EC2 instance
- demos
- early internal launch

It is not ideal for:
- multiple app instances
- autoscaling
- long-term SaaS reliability

The next backend upgrade after AWS launch should be:
- move tenant and lead data to PostgreSQL or MySQL
- move uploaded/static mutable assets to S3 if needed

## Health checks

Use:
- web: `/api/health`
- nina: `/api/health`

## Best recommendation for tomorrow

If you want the least risky launch path:

1. deploy both services on one Ubuntu EC2 instance
2. run Gunicorn for both
3. put nginx in front
4. attach HTTPS
5. fix `niharika.com` DNS to the EC2 public endpoint

That gets you live faster than trying to force a multi-service managed setup too early.


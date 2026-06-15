# Niharika Windows App

Use this folder like a simple Windows desktop app package.

Files:
- `launch-niharika-desktop.cmd` - double-click this to open Niharika in an app-style window
- `launch-niharika-desktop.ps1` - PowerShell launcher used by the `.cmd` file

What it does:
- starts the local Flask app on `http://127.0.0.1:8080`
- starts Nina on `http://127.0.0.1:5000`
- opens Microsoft Edge in app mode to `http://127.0.0.1:8080/business`

Main pages:
- Home: `http://127.0.0.1:8080/`
- Business dashboard: `http://127.0.0.1:8080/business`
- Signup: `http://127.0.0.1:8080/signup`
- Admin: `http://127.0.0.1:8080/admin`

Demo login:
- Email: `sivashankarimurugesan@niharika.com`
- Password: `DemoPass123!`
- License key: `Shown after signup or available in the seeded local demo account`

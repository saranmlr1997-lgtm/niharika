# Niharika GitHub-Ready Package

This copy is prepared for upload to GitHub or another remote repository.

Included:
- app code
- static pages
- media and catalog assets
- setup and deployment notes
- empty starter data files

Excluded from the source export:
- local secrets
- local logs
- Cloudflare runtime binary
- Python cache files
- previous customer and lead records

Before running:
1. Copy `niharika-secrets-template.ps1` to a local secrets file outside git if needed.
2. Set the contact and Google values for your own environment.
3. Start the app with `start-niharika-stack.ps1` or run `app.py` and `nina.py` manually.

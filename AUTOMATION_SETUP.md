## Reusable auth/config across projects (laptop + server)

This repo contains a reusable package: `automation_core/`.

### Install into any project (once per venv)

From repo root:

```bash
pip install -e ./automation_core
```

### Standard config layout

- **Per-project**: create a `.env` (not committed)
  - Use `ENV.example` as a template: copy it to `.env` and fill values.
- **Shared across all projects on a machine** (optional): `~/.config/automation_core/common.env`
  - Put common vars there (e.g., NOTION_API_KEY).

### Laptop setup (interactive Google OAuth)

1) Create an OAuth client in Google Cloud Console (Desktop/Installed App).
2) Download the client secrets JSON to your laptop (example path: `~/.config/automation_core/google/client_secret.json`)
3) Put the file at:
   - `~/.config/automation_core/google/client_secret.json`

> You can also override the path with `GOOGLE_OAUTH_CLIENT_SECRETS`, but if you use the default location you don’t need to set anything.

Then run the login flow once (it will open a browser and cache a refreshable token):

```bash
automation-core google-login
```

Token is cached at:
- `~/.config/automation_core/google/token.json` (override via `GOOGLE_OAUTH_TOKEN_PATH`)

### Server setup (non-interactive)

Preferred approach is a **service account**:

1) Create a service account in Google Cloud Console.
2) Download a JSON key to the server (store it as a secret).
3) Put the file at:
   - `~/.config/automation_core/google/service_account.json`

> You can also override the path with `GOOGLE_SERVICE_ACCOUNT_JSON`, but if you use the default location you don’t need to set anything.

Then in code use `auth_mode="service_account"` when creating connectors.

> If you need to access a *user's* Drive on a server (not Workspace domain-wide), you can still use the OAuth token approach, but you must securely copy `token.json` (or generate it on a machine once) and store it as a server secret.

### Example usage (in any project)

```python
from automation_core.connectors.google_drive import get_drive_service
from automation_core.connectors.google_sheets import get_sheets_service
from automation_core.connectors.notion import get_notion_client

# Laptop (OAuth)
drive = get_drive_service(auth_mode="user")

# Server (service account)
sheets = get_sheets_service(auth_mode="service_account")

notion = get_notion_client()
```


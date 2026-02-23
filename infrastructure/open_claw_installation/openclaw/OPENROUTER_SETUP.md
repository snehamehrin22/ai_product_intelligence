# OpenClaw + OpenRouter Configuration

## Current Setup

**Container**: `openclaw-dygi-openclaw-1`
**Status**: ✅ Running and configured with OpenRouter
**Web UI**: http://localhost:46326
**Gateway**: ws://127.0.0.1:18789

### Model Configuration
- **Primary Model**: `openrouter/meta-llama/llama-3.3-70b-instruct` (Llama 3.3 70B)
- **Provider**: OpenRouter
- **API Key**: Configured in auth-profiles.json

---

## Configuration Files

### 1. Docker Compose Setup
**Location**: `/docker/openclaw-dygi/docker-compose.yml`

```yaml
services:
  openclaw:
    image: ghcr.io/hostinger/hvps-openclaw:latest
    init: true
    ports:
      - "${PORT}:${PORT}"
    env_file:
      - .env
    restart: unless-stopped
    volumes:
      - ./data:/data
      - ./data/linuxbrew:/home/linuxbrew
```

### 2. Environment Variables
**Location**: `/docker/openclaw-dygi/.env`

```env
PORT=46326
TZ=America/New_York
OPENCLAW_GATEWAY_TOKEN=REDACTED
OPENROUTER_API_KEY=REDACTED
```

### 3. OpenClaw Main Config
**Location**: `/docker/openclaw-dygi/data/.openclaw/openclaw.json`

Key sections:
- `agents.defaults.model.primary`: Set to OpenRouter Llama model
- `agents.defaults.models`: Lists available models
- `gateway`: WebSocket configuration
- `plugins`: Currently only Discord is enabled

### 4. Agent Auth Profiles
**Location**: `/docker/openclaw-dygi/data/.openclaw/agents/main/auth-profiles.json`

```json
{
  "version": 1,
  "profiles": {
    "openrouter:default": {
      "provider": "openrouter",
      "type": "api_key",
      "key": "REDACTED"
    }
  }
}
```

---

## Available Models

### Currently Configured
- **Llama 3.3 70B** - `openrouter/meta-llama/llama-3.3-70b-instruct` (Primary)
- **Mistral Large** - `openrouter/mistralai/mistral-large-2512`
- **Gemini 2.0 Flash** - `openrouter/google/gemini-2.0-flash-001`

### To Add More Models
Edit `/docker/openclaw-dygi/data/.openclaw/openclaw.json`:

```json
"agents": {
  "defaults": {
    "models": {
      "openrouter/model-id": {
        "alias": "Display Name"
      }
    }
  }
}
```

Then restart the container:
```bash
cd /docker/openclaw-dygi && docker compose restart
```

---

## Running OpenClaw

### Start
```bash
cd /docker/openclaw-dygi
docker compose up -d
```

### Stop
```bash
cd /docker/openclaw-dygi
docker compose down
```

### View Logs
```bash
docker logs openclaw-dygi-openclaw-1 -f
```

### Restart
```bash
cd /docker/openclaw-dygi
docker compose restart
```

---

## Testing the Setup

### Web UI Test
1. Open http://localhost:46326
2. Try asking a question
3. Should respond using Llama 3.3 70B from OpenRouter

### Check Active Model
```bash
docker logs openclaw-dygi-openclaw-1 | grep "agent model"
```

Expected output:
```
[gateway] agent model: openrouter/meta-llama/llama-3.3-70b-instruct
```

---

## Troubleshooting

### API Key Not Found Error
If you see: `No API key found for provider "openrouter"`

**Solution**: Ensure auth-profiles.json exists at:
- `/docker/openclaw-dygi/data/.openclaw/agents/main/auth-profiles.json`

### Gateway Connection Refused
If the container crashes on startup with `ECONNREFUSED 127.0.0.1:18789`:

**Solution**: This is a known startup race condition. The container auto-restarts via `restart: unless-stopped` policy. Wait 10-15 seconds for it to stabilize.

### Model Not Responding
Check if OPENROUTER_API_KEY is valid in `.env` file and auth-profiles.json

---

## Next Steps

1. **Add Discord Integration**: Configure Discord bot token in openclaw.json
2. **Add More Channels**: Enable Slack, Telegram, etc. in plugins
3. **Customize Tools**: Configure which tools agents can use
4. **Set Up Monitoring**: Configure health checks and logging

---

## Related Documentation
- See `/docker/openclaw-dygi/` for complete setup files
- See `openclaw.json` for full configuration options
- See OpenRouter docs: https://openrouter.ai/docs

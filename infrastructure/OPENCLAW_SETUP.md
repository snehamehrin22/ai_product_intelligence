# OpenClaw Setup & Configuration

## Current Production Setup

**Status**: ✅ Running with OpenRouter + Llama 3.3 70B
**Container**: `openclaw-dygi-openclaw-1`
**Web UI**: http://localhost:46326
**Gateway**: ws://127.0.0.1:18789

---

## Quick Links

- **[OpenRouter Quick Start](./open_claw_installation/openclaw/guides/openrouter-quickstart.md)** - Get started in 5 minutes
- **[Full OpenRouter Setup](./open_claw_installation/openclaw/OPENROUTER_SETUP.md)** - Complete configuration guide
- **[Config Example Files](./open_claw_installation/config/)** - docker-compose.yml and .env templates

---

## Key Files

### Configuration
| Path | Purpose |
|------|---------|
| `/docker/openclaw-dygi/.env` | API keys and environment variables |
| `/docker/openclaw-dygi/docker-compose.yml` | Container configuration |
| `/docker/openclaw-dygi/data/.openclaw/openclaw.json` | OpenClaw settings |
| `/docker/openclaw-dygi/data/.openclaw/agents/main/auth-profiles.json` | API authentication |

### Infrastructure Docs
| File | Purpose |
|------|---------|
| `open_claw_installation/openclaw/OPENROUTER_SETUP.md` | Full technical documentation |
| `open_claw_installation/openclaw/guides/openrouter-quickstart.md` | 5-minute setup guide |
| `open_claw_installation/config/env.example` | Environment variables template |
| `open_claw_installation/config/docker-compose.example.yml` | Docker compose template |

---

## Current Models Available

### Primary Model
- **Llama 3.3 70B** (`openrouter/meta-llama/llama-3.3-70b-instruct`)
  - Best balance of performance and cost
  - Good for complex reasoning

### Fallback Models (configured)
- **Mistral Large** (`openrouter/mistralai/mistral-large-2512`)
- **Gemini 2.0 Flash** (`openrouter/google/gemini-2.0-flash-001`)

### To Switch Models
1. Edit `/docker/openclaw-dygi/data/.openclaw/openclaw.json`
2. Change `agents.defaults.model.primary` to desired model ID
3. Restart: `cd /docker/openclaw-dygi && docker compose restart`

---

## Common Commands

### Start/Stop OpenClaw
```bash
# Start
cd /docker/openclaw-dygi && docker compose up -d

# Stop
cd /docker/openclaw-dygi && docker compose down

# Restart
cd /docker/openclaw-dygi && docker compose restart
```

### View Logs
```bash
docker logs openclaw-dygi-openclaw-1 -f
```

### Access Web UI
```
http://localhost:46326
```

### Check Active Model
```bash
docker logs openclaw-dygi-openclaw-1 | grep "agent model"
```

---

## Environment Variables

See `open_claw_installation/config/env.example` for full list.

**Essential for OpenRouter**:
```env
OPENCLAW_GATEWAY_TOKEN=<gateway_token>
OPENROUTER_API_KEY=sk-or-v1-<your_key>
PORT=46326
TZ=America/New_York
```

---

## Troubleshooting

### "No API key found" Error
**Solution**: Ensure auth-profiles.json exists in:
- `/docker/openclaw-dygi/data/.openclaw/agents/main/auth-profiles.json`

### Container Won't Start
**Solution**: Wait 10-15 seconds. There's a startup race condition that auto-resolves.

### Gateway Connection Refused
**Solution**: Check container logs for errors. Restart container.

---

## Architecture

```
ai_product_intelligence/
├── infrastructure/
│   ├── open_claw_installation/
│   │   ├── openclaw/
│   │   │   ├── guides/
│   │   │   │   ├── openrouter-quickstart.md (← START HERE)
│   │   │   │   └── installation.md
│   │   │   ├── OPENROUTER_SETUP.md (← FULL DOCS)
│   │   │   └── research.md
│   │   └── config/
│   │       ├── env.example
│   │       └── docker-compose.example.yml
│   └── OPENCLAW_SETUP.md (← YOU ARE HERE)
│
└── Docker Setup:
    └── /docker/openclaw-dygi/
        ├── docker-compose.yml
        ├── .env (secrets, git-ignored)
        └── data/
            ├── .openclaw/
            │   ├── openclaw.json
            │   └── agents/main/
            │       └── auth-profiles.json
```

---

## Next Steps

### Immediate
- [ ] Test web UI: http://localhost:46326
- [ ] Verify model is responding
- [ ] Review `OPENROUTER_SETUP.md` for configuration options

### Short-term
- [ ] Add Discord integration
- [ ] Configure additional channels (Slack, Telegram)
- [ ] Set up monitoring/alerting
- [ ] Back up auth-profiles.json securely

### Long-term
- [ ] Deploy to production
- [ ] Add more specialized agents
- [ ] Integrate with your product pipeline
- [ ] Set up usage monitoring and cost alerts

---

## Security Notes

⚠️ **Never commit these files to git**:
- `.env` (contains API keys)
- `auth-profiles.json` (contains API keys)
- `.openclaw/` directory (sensitive data)

✅ **Already in .gitignore**: These should be protected

---

## Related Documentation

- [OpenRouter API Docs](https://openrouter.ai/docs)
- [OpenClaw Documentation](https://github.com/hostinger/openclaw)
- [Infrastructure README](./README.md)

---

## Questions?

Refer to:
1. `openrouter-quickstart.md` - For basic setup
2. `OPENROUTER_SETUP.md` - For detailed configuration
3. Docker logs: `docker logs openclaw-dygi-openclaw-1`

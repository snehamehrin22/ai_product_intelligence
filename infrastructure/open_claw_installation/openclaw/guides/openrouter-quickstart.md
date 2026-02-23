# OpenRouter + OpenClaw Quick Start

## 5-Minute Setup

### Step 1: Get OpenRouter API Key
1. Go to https://openrouter.ai/
2. Sign up / Log in
3. Go to Settings → API Keys
4. Copy your API key (starts with `sk-or-v1-`)

### Step 2: Create .env File
```bash
cd /docker/openclaw-dygi

# Copy the example
cp /path/to/config/env.example .env

# Edit and add your key
nano .env
```

Add to `.env`:
```env
PORT=46326
TZ=America/New_York
OPENCLAW_GATEWAY_TOKEN=REDACTED
OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE
```

### Step 3: Create Auth Profiles
```bash
mkdir -p /docker/openclaw-dygi/data/.openclaw/agents/main/agent

cat > /docker/openclaw-dygi/data/.openclaw/agents/main/auth-profiles.json << 'EOF'
{
  "version": 1,
  "profiles": {
    "openrouter:default": {
      "provider": "openrouter",
      "type": "api_key",
      "key": "sk-or-v1-YOUR_KEY_HERE"
    }
  }
}
EOF
```

Also copy to agent subdirectory:
```bash
cp /docker/openclaw-dygi/data/.openclaw/agents/main/auth-profiles.json \
   /docker/openclaw-dygi/data/.openclaw/agents/main/agent/
```

### Step 4: Start OpenClaw
```bash
cd /docker/openclaw-dygi
docker compose up -d
```

### Step 5: Test
Open http://localhost:46326 in your browser and try asking a question!

---

## Verify Setup

Check the logs:
```bash
docker logs openclaw-dygi-openclaw-1 | grep "agent model"
```

Should show:
```
[gateway] agent model: openrouter/meta-llama/llama-3.3-70b-instruct
```

---

## Switch Models

Edit `/docker/openclaw-dygi/data/.openclaw/openclaw.json`:

Find `agents.defaults.model.primary` and change to:

**Mistral Large** (Good for complex tasks):
```
"primary": "openrouter/mistralai/mistral-large-2512"
```

**Gemini 2.0 Flash** (Fast and cheap):
```
"primary": "openrouter/google/gemini-2.0-flash-001"
```

Then restart:
```bash
cd /docker/openclaw-dygi && docker compose restart
```

---

## Pricing Estimate

OpenRouter pricing (varies by model):
- **Llama 3.3 70B**: ~$0.00015 per 1K input tokens, $0.0006 per 1K output
- **Mistral Large**: ~$0.008 per 1K input, $0.024 per 1K output
- **Gemini 2.0 Flash**: ~$0.075 per 1M input, $0.3 per 1M output

👉 **Pro Tip**: Use Gemini 2.0 Flash as a fallback to save costs!

---

## Troubleshooting

**Q: "No API key found for provider openrouter"**
- A: Check that auth-profiles.json exists in both:
  - `/docker/openclaw-dygi/data/.openclaw/agents/main/auth-profiles.json`
  - `/docker/openclaw-dygi/data/.openclaw/agents/main/agent/auth-profiles.json`

**Q: Container keeps crashing**
- A: Wait 10-15 seconds - there's a startup race condition. It auto-restarts.

**Q: How do I use a different model?**
- A: Edit `openclaw.json` and change `agents.defaults.model.primary`

---

## Next: Add Discord

Edit `/docker/openclaw-dygi/data/.openclaw/openclaw.json`:

```json
"channels": {
  "discord": {
    "enabled": true,
    "token": "YOUR_DISCORD_BOT_TOKEN_HERE",
    "groupPolicy": "allowlist",
    "dmPolicy": "allowlist",
    "allowFrom": [
      "YOUR_DISCORD_USER_ID_HERE"
    ]
  }
}
```

Then restart:
```bash
cd /docker/openclaw-dygi && docker compose restart
```

---

See [OPENROUTER_SETUP.md](../OPENROUTER_SETUP.md) for full documentation.

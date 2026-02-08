# OpenClaw Quick Start Guide

## TL;DR - Fastest Installation

**Using Hostinger hPanel (5 minutes):**
```
1. Login to hPanel → VPS → Docker Manager
2. Catalog → Search "OpenClaw" → Deploy
3. Save the gateway token
4. Access http://YOUR_VPS_IP:18789
```

**Using SSH (15 minutes):**
```bash
# Download and run installation script
wget https://raw.githubusercontent.com/openclaw/openclaw/main/docker-setup.sh
chmod +x docker-setup.sh
./docker-setup.sh

# Access dashboard
http://YOUR_VPS_IP:18789
```

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Hostinger VPS with Ubuntu 22.04/24.04
- [ ] At least 2GB RAM, 10GB storage
- [ ] SSH access credentials
- [ ] At least ONE AI provider API key:
  - [ ] Anthropic: https://console.anthropic.com/
  - [ ] OpenAI: https://platform.openai.com/
  - [ ] Gemini: https://ai.google.dev/

---

## Installation Path A: Hostinger One-Click

### Step 1: Access Docker Manager
1. Go to https://hpanel.hostinger.com/
2. Click your VPS
3. Click "Docker Manager"
4. If not installed, click "Install Docker Manager" (wait 2-3 min)

### Step 2: Deploy OpenClaw
1. Click "Catalog" tab
2. Search "OpenClaw"
3. Click the OpenClaw card
4. Click "Deploy"

### Step 3: Configure
1. **Copy the Gateway Token** (starts with `oct_`)
2. Add your API keys:
   - Click "Add Variable"
   - Name: `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY`)
   - Value: Your API key
3. Click "Save"
4. Click "Deploy"

### Step 4: Access
1. Wait for "Running" status (green)
2. Open: `http://YOUR_VPS_IP:18789`
3. Enter gateway token
4. Complete onboarding

**Done!** You can now use OpenClaw.

---

## Installation Path B: Manual via SSH

### Quick Script Installation
```bash
# Connect to VPS
ssh root@YOUR_VPS_IP

# Download installation script
wget -O install_openclaw.sh https://path-to-your-script/install_openclaw.sh
chmod +x install_openclaw.sh

# Run installation
sudo ./install_openclaw.sh
```

The script will:
- Install Docker & Docker Compose
- Clone OpenClaw repository
- Run setup wizard
- Configure firewall
- Start OpenClaw

### Manual Step-by-Step
```bash
# 1. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Install Docker Compose
sudo apt install docker-compose-plugin -y

# 3. Clone OpenClaw
cd /opt
sudo git clone https://github.com/openclaw/openclaw.git
cd openclaw

# 4. Run setup
chmod +x docker-setup.sh
./docker-setup.sh

# 5. Allow firewall
sudo ufw allow 18789/tcp
```

---

## First-Time Setup

### 1. Access Dashboard
```
http://YOUR_VPS_IP:18789
```

### 2. Enter Gateway Token
Use the token saved during installation (starts with `oct_`)

### 3. Choose AI Model
Select from:
- Claude Sonnet 3.5 (Recommended)
- GPT-4o
- Gemini Pro

### 4. Test Connection
Send a message:
```
Hello, introduce yourself
```

You should get an AI response.

---

## Connect Messaging Platforms

### Telegram (Easiest)

**1. Create Bot:**
- Open Telegram
- Search for `@BotFather`
- Send `/newbot`
- Follow prompts
- Copy the token (format: `123456789:ABC...`)

**2. Add to OpenClaw:**
```bash
cd /opt/openclaw
docker compose run --rm openclaw-cli providers add \
  --provider telegram \
  --token "YOUR_BOT_TOKEN"
```

**3. Test:**
- Search for your bot in Telegram
- Send `/start`
- Send "Hello"
- Get AI response

### WhatsApp

**Via Dashboard:**
1. Dashboard → Integrations → WhatsApp
2. Click "Connect WhatsApp"
3. Scan QR code with WhatsApp app
4. Wait for confirmation
5. Send test message

### Discord

**1. Create Bot:**
- Go to https://discord.com/developers/applications
- New Application → Bot → Add Bot
- Copy token

**2. Add to OpenClaw:**
```bash
docker compose run --rm openclaw-cli providers add \
  --provider discord \
  --token "YOUR_DISCORD_TOKEN"
```

**3. Invite to Server:**
- OAuth2 → URL Generator
- Scopes: `bot`
- Permissions: `Send Messages`, `Read Message History`
- Open generated URL → Select server

---

## Essential Commands

### Docker Management
```bash
# Navigate to OpenClaw directory
cd /opt/openclaw

# View status
docker compose ps

# View logs
docker compose logs -f

# Restart
docker compose restart

# Stop
docker compose down

# Start
docker compose up -d

# Rebuild
docker compose build && docker compose up -d
```

### OpenClaw CLI
```bash
# Health check
docker compose run --rm openclaw-cli doctor

# List providers
docker compose run --rm openclaw-cli providers list

# View config
docker compose run --rm openclaw-cli config show

# Regenerate token
docker compose run --rm openclaw-cli auth regenerate-token
```

### System Monitoring
```bash
# Check resources
docker stats

# Check disk space
df -h

# View firewall
sudo ufw status

# Check port 18789
netstat -tlnp | grep 18789
```

---

## Common Issues & Fixes

### Cannot Access Dashboard

**Problem:** Browser shows "Connection refused"

**Solution:**
```bash
# Check if running
docker compose ps

# If not running, start it
docker compose up -d

# Check firewall
sudo ufw allow 18789/tcp

# Check logs
docker compose logs openclaw-gateway
```

### Invalid Gateway Token

**Problem:** Token not accepted

**Solution:**
```bash
# Retrieve token from config
cat ~/.openclaw/config.json | grep gatewayToken

# Or regenerate
docker compose run --rm openclaw-cli auth regenerate-token
```

### API Key Not Working

**Problem:** "Invalid API key" errors

**Solution:**
```bash
# Update API key
docker compose run --rm openclaw-cli config set \
  providers.anthropic.apiKey "NEW_KEY"

# Restart
docker compose restart
```

### Out of Memory

**Problem:** Container crashes, slow performance

**Solution:**
```bash
# Check usage
docker stats

# Upgrade VPS to 4GB+ RAM
# Or limit Docker memory in docker-compose.yml
```

### Telegram Bot Not Responding

**Problem:** Bot online but doesn't reply

**Solution:**
```bash
# Check logs
docker compose logs | grep telegram

# Remove and re-add
docker compose run --rm openclaw-cli providers remove telegram
docker compose run --rm openclaw-cli providers add \
  --provider telegram --token "YOUR_TOKEN"

# Restart
docker compose restart
```

---

## Security Checklist

After installation:

- [ ] Change default port (edit docker-compose.yml)
- [ ] Set up reverse proxy with SSL (Nginx + Let's Encrypt)
- [ ] Restrict port 18789 by IP (UFW rules)
- [ ] Store gateway token in password manager
- [ ] Enable UFW firewall
- [ ] Keep system updated: `sudo apt update && sudo apt upgrade`
- [ ] Regular backups of `~/.openclaw/` directory

---

## Next Steps

### Basic Usage
1. Ask AI questions via dashboard
2. Connect your preferred messaging app
3. Start automating tasks

### Advanced Configuration
1. Add multiple AI providers
2. Set up custom skills/plugins
3. Configure webhooks
4. Integrate with other services (50+ available)

### Optimization
1. Set up domain with SSL
2. Configure monitoring (optional)
3. Create backup automation
4. Tune AI parameters (temperature, max tokens)

---

## Getting Help

**Resources:**
- Full Guide: `INSTALLATION_GUIDE.md` (same directory)
- Official Docs: https://docs.openclaw.ai/
- GitHub: https://github.com/openclaw/openclaw
- Community: Check official website for Discord/forum links

**Common Questions:**
- Q: Which AI provider is best?
  A: Claude Sonnet 3.5 for best results, GPT-4o for speed, Gemini for cost

- Q: Can I use multiple messaging platforms?
  A: Yes! Connect as many as you want

- Q: Is my data private?
  A: Yes, everything runs on your VPS. AI providers see your queries only

- Q: How much does it cost?
  A: VPS: $6-15/mo (Hostinger), AI API: Pay-per-use (varies)

---

## Update Your Installation

```bash
cd /opt/openclaw
git pull origin main
docker compose build
docker compose down
docker compose up -d
```

Check for updates monthly.

---

**Installation Time:** 5-20 minutes
**Difficulty:** Easy to Moderate
**Cost:** ~$10-20/month (VPS + API usage)

**Ready to start?** Follow Path A (Hostinger) or Path B (SSH) above.

For detailed explanations, see: `INSTALLATION_GUIDE.md`

# OpenClaw Installation Guide for Hostinger VPS

## Table of Contents
1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Prerequisites](#prerequisites)
4. [Installation Path A: Hostinger One-Click (Recommended)](#installation-path-a-hostinger-one-click-recommended)
5. [Installation Path B: Manual Docker Setup](#installation-path-b-manual-docker-setup)
6. [Post-Installation Configuration](#post-installation-configuration)
7. [Connecting Messaging Channels](#connecting-messaging-channels)
8. [Security Hardening](#security-hardening)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance & Updates](#maintenance--updates)

---

## Overview

OpenClaw is a self-hosted personal AI assistant that runs on your VPS and connects to multiple messaging platforms (WhatsApp, Telegram, Discord, Slack, Signal, iMessage). This guide covers installation on Hostinger VPS.

**What OpenClaw Does:**
- Personal AI assistant accessible via your favorite messaging apps
- Full system access (file operations, shell commands, web browsing)
- Supports multiple AI providers (Anthropic Claude, OpenAI GPT, Gemini, local models)
- Persistent memory and context retention
- Extensible via skills and plugins (50+ integrations)

---

## System Requirements

### Minimum Specifications
- **CPU:** 1-2 vCPU
- **RAM:** 2GB (sufficient for basic usage)
- **Storage:** 10GB+ (SSD strongly recommended)
- **OS:** Ubuntu 22.04 or 24.04 LTS
- **Network:** Port 18789 must be accessible

### Recommended Specifications (Better Performance)
- **CPU:** 2+ vCPU
- **RAM:** 4GB (for stable dashboard and concurrent tasks)
- **Storage:** 20GB+ SSD
- **OS:** Ubuntu 24.04 LTS

### Hostinger VPS Plans
- **KVM 1:** 2 vCPU, 4GB RAM, 50GB SSD (Recommended minimum)
- **KVM 2+:** Better performance for heavier workloads

---

## Prerequisites

### Required Before Starting

1. **Hostinger VPS Account**
   - Active VPS with SSH access
   - Root or sudo privileges
   - VPS IP address

2. **AI Provider API Keys (At Least One)**
   - Anthropic API key: https://console.anthropic.com/
   - OpenAI API key: https://platform.openai.com/
   - Google Gemini API key: https://ai.google.dev/
   - XAI API key: https://x.ai/

3. **SSH Client**
   - Terminal (macOS/Linux)
   - PuTTY or Windows Terminal (Windows)

4. **Optional but Recommended**
   - Domain name pointed to VPS IP
   - SSL certificate (for HTTPS access)
   - Messaging platform credentials (Telegram bot token, WhatsApp number, etc.)

### Gather This Information
Create a secure note with:
```
VPS IP: _________________
SSH Username: root (or your sudo user)
SSH Password/Key: _________________

API Keys:
- Anthropic: _________________
- OpenAI: _________________
- Gemini: _________________

Messaging:
- Telegram Bot Token: _________________
- WhatsApp Number: _________________
```

---

## Installation Path A: Hostinger One-Click (Recommended)

**Time Required:** 15-20 minutes
**Difficulty:** Easy
**Best For:** Quick setup with minimal configuration

### Step 1: Access Hostinger hPanel

1. Log in to your Hostinger account: https://hpanel.hostinger.com/
2. Navigate to **VPS** section
3. Select your VPS instance
4. Click **Docker Manager**

### Step 2: Install Docker Manager (If Not Installed)

1. If Docker Manager is not yet installed, click **Install Docker Manager**
2. Wait for installation to complete (2-3 minutes)
3. Verify installation shows "Docker Manager Active"

### Step 3: Deploy OpenClaw from Catalog

1. In Docker Manager, click **Catalog** tab
2. Search for "**OpenClaw**" in the search bar
3. Click on the OpenClaw application card
4. Click **Deploy** button

### Step 4: Configure Environment Variables

**Required Variable:**
- `OPENCLAW_GATEWAY_TOKEN`: Auto-generated (save this securely!)

**Optional Variables (Add Your API Keys):**
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
GOOGLE_API_KEY=xxxxxxxxxxxxx
XAI_API_KEY=xxxxxxxxxxxxx
```

**Optional Messaging Variables:**
```
WHATSAPP_NUMBER=+1234567890
```

**Configuration Steps:**
1. Click **Environment Variables** section
2. Note the auto-generated `OPENCLAW_GATEWAY_TOKEN` (copy and save securely)
3. Click **Add Variable** for each API key you want to include
4. Enter variable name and value
5. Click **Save**

### Step 5: Deploy and Start

1. Review configuration summary
2. Click **Deploy** button
3. Wait for deployment (3-5 minutes)
4. Check deployment status: should show "Running" with green indicator

### Step 6: Access OpenClaw Web Interface

1. Find the assigned port (usually 18789)
2. Open browser and navigate to:
   ```
   http://YOUR_VPS_IP:18789
   ```
3. Enter the `OPENCLAW_GATEWAY_TOKEN` when prompted
4. You should see the OpenClaw dashboard

### Step 7: Initial Configuration

1. **Select AI Provider:** Choose your preferred AI model (Claude, GPT-4, etc.)
2. **Verify API Keys:** Test connection to your AI provider
3. **Set Preferences:** Configure language, timezone, default behaviors
4. **Test Basic Commands:** Try a simple query like "Hello, who are you?"

**Success Indicator:** You receive a response from the AI assistant.

---

## Installation Path B: Manual Docker Setup

**Time Required:** 30-45 minutes
**Difficulty:** Intermediate
**Best For:** Custom configurations, learning, or if Path A is unavailable

### Step 1: Connect to VPS via SSH

**From Terminal (macOS/Linux):**
```bash
ssh root@YOUR_VPS_IP
```

**From Windows (PowerShell):**
```powershell
ssh root@YOUR_VPS_IP
```

Enter your password when prompted.

### Step 2: Update System Packages

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 3: Install Docker and Docker Compose

**Install Docker:**
```bash
# Install prerequisites
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

**Verify Installation:**
```bash
docker --version
docker compose version
```

Expected output:
```
Docker version 24.0.x, build xxxxx
Docker Compose version v2.x.x
```

### Step 4: Install Git

```bash
sudo apt install -y git
```

### Step 5: Clone OpenClaw Repository

```bash
# Navigate to a suitable directory
cd /opt

# Clone the repository
sudo git clone https://github.com/openclaw/openclaw.git

# Change ownership
sudo chown -R $USER:$USER openclaw

# Enter directory
cd openclaw
```

### Step 6: Run Docker Setup Script

```bash
chmod +x docker-setup.sh
./docker-setup.sh
```

**What This Script Does:**
1. Builds the OpenClaw Docker image
2. Runs the onboarding wizard
3. Generates a gateway token
4. Creates configuration directories
5. Starts the Docker Compose gateway

### Step 7: Complete Onboarding Wizard

The script will launch an interactive wizard. Follow the prompts:

1. **API Provider Selection:**
   ```
   Which AI provider would you like to use?
   1) Anthropic (Claude)
   2) OpenAI (GPT)
   3) Google (Gemini)
   4) Other

   Selection: 1
   ```

2. **Enter API Key:**
   ```
   Enter your Anthropic API key: sk-ant-xxxxxxxxxxxxx
   ```

3. **Model Selection:**
   ```
   Which model would you like to use?
   1) Claude Sonnet 3.5
   2) Claude Opus
   3) Claude Haiku

   Selection: 1
   ```

4. **Security Settings:**
   ```
   Enable sandbox mode? (recommended) [Y/n]: Y
   ```

5. **Gateway Token Generation:**
   ```
   Generated gateway token: oct_xxxxxxxxxxxxxxxxxxxx

   IMPORTANT: Save this token securely. You'll need it to access the dashboard.
   ```
   **Copy and save this token immediately!**

### Step 8: Verify Docker Containers

```bash
docker compose ps
```

Expected output:
```
NAME                    STATUS    PORTS
openclaw-gateway        Up        0.0.0.0:18789->18789/tcp
```

**Check Logs (If Issues):**
```bash
docker compose logs openclaw-gateway
```

### Step 9: Configure Firewall

**Allow Port 18789:**
```bash
sudo ufw allow 18789/tcp
sudo ufw enable
sudo ufw status
```

### Step 10: Access Web Interface

1. Open browser: `http://YOUR_VPS_IP:18789`
2. Enter gateway token when prompted
3. Complete initial setup

---

## Post-Installation Configuration

### Access the Dashboard

```
http://YOUR_VPS_IP:18789
```

Enter your gateway token to log in.

### Verify Installation Health

**Run Health Check:**
```bash
# Via CLI (if installed locally)
openclaw doctor

# Via Docker
docker compose run --rm openclaw-cli doctor
```

**Expected Output:**
```
✓ Gateway running
✓ API credentials configured
✓ Network connectivity OK
✓ Storage permissions OK
```

### Configure Additional AI Providers

**Add Secondary API Keys:**

1. Navigate to **Settings** → **AI Providers**
2. Click **Add Provider**
3. Select provider (OpenAI, Gemini, etc.)
4. Enter API key
5. Test connection
6. Save

**Or via CLI:**
```bash
docker compose run --rm openclaw-cli config set providers.openai.apiKey "sk-proj-xxxxx"
```

### Set Default Model

**Via Dashboard:**
1. Settings → AI Providers
2. Select preferred model
3. Click "Set as Default"

**Via CLI:**
```bash
docker compose run --rm openclaw-cli config set defaultModel "claude-sonnet-3.5"
```

---

## Connecting Messaging Channels

### Telegram Bot

**Step 1: Create Telegram Bot**
1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow prompts to name your bot
4. Copy the bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Step 2: Add to OpenClaw**

**Via Dashboard:**
1. Settings → Integrations → Telegram
2. Paste bot token
3. Click "Connect"

**Via CLI:**
```bash
docker compose run --rm openclaw-cli providers add \
  --provider telegram \
  --token "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
```

**Step 3: Test**
1. Open Telegram
2. Search for your bot username
3. Send `/start`
4. Send a message like "Hello"
5. Bot should respond with AI-generated message

### WhatsApp

**Requirements:**
- WhatsApp number (can be different from your personal number)
- QR code scanning

**Steps:**
1. Dashboard → Integrations → WhatsApp
2. Click "Connect WhatsApp"
3. Scan QR code with WhatsApp mobile app
4. Wait for connection confirmation
5. Test by sending a message to the connected number

### Discord

**Step 1: Create Discord Bot**
1. Visit https://discord.com/developers/applications
2. Click "New Application"
3. Name your application
4. Go to **Bot** section
5. Click "Add Bot"
6. Copy bot token

**Step 2: Add to OpenClaw**
```bash
docker compose run --rm openclaw-cli providers add \
  --provider discord \
  --token "YOUR_DISCORD_BOT_TOKEN"
```

**Step 3: Invite Bot to Server**
1. Go to OAuth2 → URL Generator
2. Select scopes: `bot`
3. Select permissions: `Send Messages`, `Read Message History`
4. Copy generated URL
5. Open in browser and select server

### Slack

1. Create Slack app: https://api.slack.com/apps
2. Add Bot Token Scopes: `chat:write`, `im:read`, `im:write`
3. Install app to workspace
4. Copy Bot User OAuth Token
5. Add to OpenClaw via Dashboard or CLI

---

## Security Hardening

### 1. Change Default Port (Optional)

**Edit docker-compose.yml:**
```yaml
services:
  openclaw-gateway:
    ports:
      - "8080:18789"  # Change 8080 to your preferred port
```

Restart:
```bash
docker compose down
docker compose up -d
```

### 2. Set Up Reverse Proxy with Nginx + SSL

**Install Nginx:**
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

**Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/openclaw
```

**Add Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:18789;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Enable Site:**
```bash
sudo ln -s /etc/nginx/sites-available/openclaw /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Install SSL Certificate:**
```bash
sudo certbot --nginx -d your-domain.com
```

**Access via HTTPS:**
```
https://your-domain.com
```

### 3. Restrict Access by IP (Optional)

**Edit Nginx Config:**
```nginx
location / {
    allow YOUR_HOME_IP;
    allow YOUR_OFFICE_IP;
    deny all;

    proxy_pass http://localhost:18789;
    # ... rest of proxy settings
}
```

### 4. Enable Firewall Rules

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 5. Secure Gateway Token

**Best Practices:**
- Store in password manager (1Password, Bitwarden, etc.)
- Never commit to version control
- Regenerate periodically
- Use unique token per environment

**Regenerate Token (If Compromised):**
```bash
docker compose run --rm openclaw-cli auth regenerate-token
```

### 6. Regular Security Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update OpenClaw
cd /opt/openclaw
git pull origin main
docker compose build
docker compose up -d
```

---

## Troubleshooting

### Issue 1: Cannot Access Dashboard at Port 18789

**Symptoms:**
- Browser shows "Connection refused" or timeout
- Cannot load http://VPS_IP:18789

**Solutions:**

1. **Verify Container is Running:**
   ```bash
   docker compose ps
   ```
   Should show "Up" status.

2. **Check Firewall:**
   ```bash
   sudo ufw status
   ```
   Ensure port 18789 is allowed:
   ```bash
   sudo ufw allow 18789/tcp
   ```

3. **Check Container Logs:**
   ```bash
   docker compose logs openclaw-gateway
   ```
   Look for errors.

4. **Verify Port Binding:**
   ```bash
   netstat -tlnp | grep 18789
   ```
   Should show Docker process listening.

5. **Restart Containers:**
   ```bash
   docker compose restart
   ```

### Issue 2: Gateway Token Not Accepted

**Symptoms:**
- "Invalid token" error on login
- Token rejected despite correct copy/paste

**Solutions:**

1. **Retrieve Token from Config:**
   ```bash
   cat ~/.openclaw/config.json | grep gatewayToken
   ```

2. **Regenerate Token:**
   ```bash
   docker compose run --rm openclaw-cli auth regenerate-token
   ```
   Update your saved credentials.

3. **Check for Whitespace:**
   - Ensure no extra spaces before/after token
   - Re-copy directly from source

### Issue 3: API Key Errors

**Symptoms:**
- "Invalid API key" errors
- "Unauthorized" responses from AI provider

**Solutions:**

1. **Verify API Key Format:**
   - Anthropic: `sk-ant-xxxxx`
   - OpenAI: `sk-proj-xxxxx` or `sk-xxxxx`
   - Gemini: Standard API key format

2. **Test API Key Directly:**
   ```bash
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: YOUR_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "content-type: application/json" \
     -d '{"model":"claude-3-sonnet-20240229","max_tokens":1024,"messages":[{"role":"user","content":"Hello"}]}'
   ```

3. **Update API Key in OpenClaw:**
   ```bash
   docker compose run --rm openclaw-cli config set providers.anthropic.apiKey "NEW_KEY"
   docker compose restart
   ```

### Issue 4: Telegram Bot Not Responding

**Symptoms:**
- Bot shows online but doesn't respond
- Messages sent but no reply

**Solutions:**

1. **Verify Bot Token:**
   ```bash
   docker compose run --rm openclaw-cli config get providers.telegram.token
   ```

2. **Check Bot Logs:**
   ```bash
   docker compose logs openclaw-gateway | grep telegram
   ```

3. **Re-add Telegram Provider:**
   ```bash
   docker compose run --rm openclaw-cli providers remove telegram
   docker compose run --rm openclaw-cli providers add --provider telegram --token "YOUR_TOKEN"
   ```

4. **Test Webhook:**
   ```bash
   curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe
   ```

### Issue 5: High Memory Usage / Performance Issues

**Symptoms:**
- Dashboard slow or unresponsive
- High RAM usage (>90%)
- Container crashes or restarts

**Solutions:**

1. **Check Resource Usage:**
   ```bash
   docker stats
   ```

2. **Increase VPS Resources:**
   - Upgrade to higher Hostinger plan (4GB+ RAM)

3. **Limit Docker Memory:**
   Edit `docker-compose.yml`:
   ```yaml
   services:
     openclaw-gateway:
       mem_limit: 2g
       memswap_limit: 2g
   ```

4. **Clear Logs:**
   ```bash
   docker compose down
   rm -rf ~/.openclaw/logs/*
   docker compose up -d
   ```

5. **Disable Unused Integrations:**
   - Dashboard → Integrations
   - Disable channels you don't use

### Issue 6: Docker Build Fails

**Symptoms:**
- `docker build` errors
- "No space left on device"
- Build timeouts

**Solutions:**

1. **Clear Docker Cache:**
   ```bash
   docker system prune -a
   ```

2. **Check Disk Space:**
   ```bash
   df -h
   ```
   If low, expand VPS storage or clean up:
   ```bash
   sudo apt autoremove
   sudo apt clean
   ```

3. **Manual Build with Verbose Output:**
   ```bash
   docker build -t openclaw:local -f Dockerfile . --progress=plain
   ```

### Issue 7: Cannot Connect WhatsApp

**Symptoms:**
- QR code won't scan
- Connection timeout
- "Already logged in elsewhere" error

**Solutions:**

1. **Ensure Phone is Connected:**
   - WhatsApp on phone must have internet
   - Phone and VPS should both be online

2. **Clear WhatsApp Session:**
   ```bash
   rm -rf ~/.openclaw/whatsapp-session
   docker compose restart
   ```

3. **Try Different Browser:**
   - Some browsers have issues with QR display
   - Try Chrome/Firefox

4. **Check WhatsApp Web Status:**
   - Open WhatsApp on phone
   - Go to Settings → Linked Devices
   - Remove any old OpenClaw sessions
   - Try scanning QR again

---

## Maintenance & Updates

### Regular Maintenance Tasks

**Weekly:**
- Check disk space: `df -h`
- Review logs for errors: `docker compose logs --tail=100`
- Verify all messaging channels are responding

**Monthly:**
- Update system packages: `sudo apt update && sudo apt upgrade -y`
- Update OpenClaw (see below)
- Review API usage and costs
- Backup configuration (see below)

### Update OpenClaw

**Check for Updates:**
```bash
cd /opt/openclaw
git fetch origin
git status
```

**Apply Updates:**
```bash
cd /opt/openclaw
git pull origin main
docker compose build
docker compose down
docker compose up -d
```

**Verify Update:**
```bash
docker compose logs openclaw-gateway | head -20
```
Check version in logs.

### Backup Configuration

**What to Backup:**
- Gateway token
- API keys
- Configuration files
- Chat history (optional)

**Backup Script:**
```bash
#!/bin/bash
BACKUP_DIR="/root/openclaw-backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/openclaw_backup_$DATE.tar.gz \
  ~/.openclaw/config.json \
  ~/.openclaw/providers.json \
  /opt/openclaw/docker-compose.yml

echo "Backup created: $BACKUP_DIR/openclaw_backup_$DATE.tar.gz"
```

**Restore from Backup:**
```bash
tar -xzf openclaw_backup_YYYYMMDD_HHMMSS.tar.gz -C /
docker compose restart
```

### Monitor Resource Usage

**Install Monitoring (Optional):**
```bash
# Install htop for interactive monitoring
sudo apt install -y htop

# Run
htop
```

**Monitor Docker Containers:**
```bash
# Real-time stats
docker stats

# Check container health
docker compose ps
```

### Logs Management

**View Logs:**
```bash
# Last 100 lines
docker compose logs --tail=100

# Follow live logs
docker compose logs -f

# Specific service
docker compose logs openclaw-gateway

# Save logs to file
docker compose logs > openclaw_logs_$(date +%Y%m%d).txt
```

**Rotate/Clear Old Logs:**
```bash
# Clear all logs
docker compose down
rm -rf ~/.openclaw/logs/*
docker compose up -d

# Or configure log rotation in docker-compose.yml
```

### Uninstall OpenClaw (If Needed)

**Complete Removal:**
```bash
# Stop and remove containers
cd /opt/openclaw
docker compose down -v

# Remove images
docker rmi openclaw:local openclaw-sandbox:bookworm-slim

# Remove repository
cd /opt
sudo rm -rf openclaw

# Remove configuration
rm -rf ~/.openclaw

# Optional: Remove Docker
sudo apt remove -y docker-ce docker-ce-cli containerd.io
sudo apt autoremove -y
```

---

## Additional Resources

### Official Documentation
- OpenClaw Docs: https://docs.openclaw.ai/
- GitHub Repository: https://github.com/openclaw/openclaw
- Community Discord: Check official website for invite link

### Hostinger Resources
- Hostinger VPS Tutorial: https://www.hostinger.com/tutorials/vps
- Docker Manager Guide: https://www.hostinger.com/tutorials/docker
- Support: https://www.hostinger.com/support

### API Provider Documentation
- Anthropic Claude: https://docs.anthropic.com/
- OpenAI GPT: https://platform.openai.com/docs
- Google Gemini: https://ai.google.dev/docs

### Messaging Platforms
- Telegram Bot API: https://core.telegram.org/bots/api
- WhatsApp Business API: https://developers.facebook.com/docs/whatsapp
- Discord Developer: https://discord.com/developers/docs

---

## Quick Reference Commands

### Essential Docker Commands
```bash
# Start containers
docker compose up -d

# Stop containers
docker compose down

# Restart containers
docker compose restart

# View running containers
docker compose ps

# View logs
docker compose logs -f

# Rebuild and restart
docker compose build && docker compose up -d

# Check resource usage
docker stats

# Clean up unused resources
docker system prune -a
```

### OpenClaw CLI Commands
```bash
# Health check
docker compose run --rm openclaw-cli doctor

# View status
docker compose run --rm openclaw-cli status

# Regenerate gateway token
docker compose run --rm openclaw-cli auth regenerate-token

# Add provider
docker compose run --rm openclaw-cli providers add --provider telegram --token "TOKEN"

# List providers
docker compose run --rm openclaw-cli providers list

# Remove provider
docker compose run --rm openclaw-cli providers remove telegram
```

### System Maintenance
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
htop

# Check firewall status
sudo ufw status

# View system logs
sudo journalctl -xe
```

---

## Support

If you encounter issues not covered in this guide:

1. Check OpenClaw GitHub Issues: https://github.com/openclaw/openclaw/issues
2. Review Docker logs for specific error messages
3. Consult Hostinger VPS support for infrastructure issues
4. Join OpenClaw community channels for peer support

---

**Document Version:** 1.0
**Last Updated:** 2026-02-07
**For:** Hostinger VPS Deployment
**OpenClaw Version:** Latest (as of 2026)

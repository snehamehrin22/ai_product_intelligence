# VPS AI Setup Guide

Complete setup for OpenClaw (messaging AI) and Claude Code (terminal AI) on Hostinger VPS.

## 📁 Structure

```
open_claw_installation/
├── README.md                    # You are here
│
├── openclaw/                    # OpenClaw setup
│   ├── guides/
│   │   ├── installation.md      # Complete guide
│   │   └── quickstart.md        # 10-minute setup
│   ├── scripts/
│   │   └── install.sh           # Automated installer
│   └── research.md              # Tech research
│
├── claude-code/                 # Claude Code setup
│   ├── guides/
│   │   ├── installation.md      # Complete guide
│   │   └── quickstart.md        # 5-minute setup
│   └── scripts/
│       └── install.sh           # Automated installer
│
├── security/                    # Security hardening
│   ├── guides/
│   │   └── security-hardening.md
│   └── scripts/
│       └── harden.sh            # Automated setup
│
├── user-setup/                  # User account setup
│   ├── guides/
│   │   ├── user-setup.md        # Complete guide
│   │   └── quickstart.md        # 10-minute setup
│   └── scripts/
│       └── setup-user.sh        # Automated setup
│
└── config/                      # Config templates
    ├── env.example              # Environment vars
    └── gitignore                # Git ignore template
```

---

## 🚀 Quick Start

### I Want To...

**Install OpenClaw (Messaging AI)**
```bash
cd openclaw/scripts
chmod +x install.sh
./install.sh
```
📖 [Quick Guide](openclaw/guides/quickstart.md) | [Full Guide](openclaw/guides/installation.md)

---

**Install Claude Code (Terminal AI)**
```bash
cd claude-code/scripts
chmod +x install.sh
./install.sh
```
📖 [Quick Guide](claude-code/guides/quickstart.md) | [Full Guide](claude-code/guides/installation.md)

---

**Secure My VPS**
```bash
cd security/scripts
chmod +x harden.sh
sudo ./harden.sh
```
📖 [Security Guide](security/guides/security-hardening.md)

---

**Set Up User Account**
```bash
cd user-setup/scripts
chmod +x setup-user.sh
sudo ./setup-user.sh
```
📖 [Quick Guide](user-setup/guides/quickstart.md) | [Full Guide](user-setup/guides/user-setup.md)

---

## 📋 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 vCPU | 2+ vCPU |
| RAM | 4GB | 8GB |
| Storage | 20GB SSD | 50GB+ SSD |
| OS | Ubuntu 22.04+ | Ubuntu 24.04 LTS |

**Recommended VPS:** Hostinger KVM 1 (2 vCPU, 4GB RAM, 50GB SSD) - $6-8/month

---

## 🎯 What Each Tool Does

### OpenClaw
**What:** AI assistant via messaging apps (WhatsApp, Telegram, Discord, etc.)
**Use:** Chat with AI from your phone
**Requires:** API key (Anthropic, OpenAI, or free Gemini)
**Access:** Web dashboard + messaging apps

### Claude Code
**What:** AI coding assistant in terminal
**Use:** Get coding help via command line
**Requires:** Claude Pro/Max subscription
**Access:** SSH terminal only

### Both Work Together!
- OpenClaw: Always-on Docker service
- Claude Code: On-demand in tmux sessions
- Both run on same 4GB VPS comfortably

---

## ⚡ Installation Order

**Recommended sequence:**

1. **OpenClaw** (20 min)
   - Run `openclaw/scripts/install.sh`
   - Configure API keys
   - Connect messaging platforms

2. **Security** (15 min)
   - Run `security/scripts/harden.sh`
   - Set up firewall
   - Configure SSL (if you have domain)

3. **User Setup** (10 min)
   - Run `user-setup/scripts/setup-user.sh`
   - Create regular user account
   - Configure Git

4. **Claude Code** (10 min)
   - SSH as regular user
   - Run `claude-code/scripts/install.sh`
   - Authenticate

**Total Time:** ~1 hour for complete setup

---

## 📚 Detailed Guides

### OpenClaw
- **[Quickstart](openclaw/guides/quickstart.md)** - Get running in 10 minutes
- **[Installation Guide](openclaw/guides/installation.md)** - Complete 400+ line guide
- **[Research](openclaw/research.md)** - Technical analysis

### Claude Code
- **[Quickstart](claude-code/guides/quickstart.md)** - Get running in 5 minutes
- **[Installation Guide](claude-code/guides/installation.md)** - Complete guide with auth
- Automated installer: `claude-code/scripts/install.sh`

### Security
- **[Security Hardening](security/guides/security-hardening.md)** - Complete security guide
  - Firewall setup
  - SSL/HTTPS configuration
  - SSH hardening
  - Fail2Ban setup
  - Automated backups
- Automated script: `security/scripts/harden.sh`

### User Setup
- **[Quickstart](user-setup/guides/quickstart.md)** - 10-minute user setup
- **[User Setup Guide](user-setup/guides/user-setup.md)** - Complete multi-user guide
  - Create user with sudo
  - Git configuration
  - GitHub SSH setup
  - Claude Code for user
- Automated script: `user-setup/scripts/setup-user.sh`

---

## 💰 Cost Breakdown

### VPS Hosting
- Hostinger KVM 1: $6-8/month ✓ Recommended
- Hostinger KVM 2: $12-15/month (heavier use)

### API Costs (OpenClaw)
- **Google Gemini:** FREE tier (60 RPM)
- Anthropic Claude: ~$3 per 1M tokens
- OpenAI GPT-4o: ~$2.50 per 1M tokens

### Claude Code
- Included with Claude Pro ($20/mo) or Max ($30/mo)

**Total: $10-40/month** depending on usage

---

## 🛠️ Quick Commands

### OpenClaw
```bash
# Check status
cd /opt/openclaw && docker compose ps

# View logs
docker compose logs -f

# Restart
docker compose restart
```

### Claude Code
```bash
# Start
claude

# With tmux
tmux new -s claude
claude

# Detach: Ctrl+B then D
# Reattach: tmux attach -t claude
```

### Git
```bash
git pull          # Get latest
git add .         # Stage changes
git commit -m ""  # Commit
git push          # Push to GitHub
```

---

## 🔐 Security Checklist

After installation:

- [ ] Firewall configured (UFW)
- [ ] SSL/HTTPS set up (with domain)
- [ ] SSH hardened (key-based auth, no root login)
- [ ] Fail2Ban protecting SSH
- [ ] Automatic updates enabled
- [ ] Daily backups configured
- [ ] OpenClaw bound to localhost only
- [ ] Nginx reverse proxy set up

**Run:** `security/scripts/harden.sh` to automate most of this

---

## 🆘 Troubleshooting

### Common Issues

**Can't access OpenClaw dashboard:**
```bash
sudo ufw allow 18789/tcp
docker compose ps  # Check if running
```

**Claude command not found:**
```bash
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc
```

**Git push fails:**
```bash
ssh -T git@github.com  # Test connection
# Re-add SSH key if needed
```

**Port already in use:**
```bash
sudo netstat -tlnp | grep 18789
# Kill process or change port
```

---

## 📖 Additional Resources

- **OpenClaw:** https://docs.openclaw.ai/
- **Claude Code:** https://code.claude.com/docs/
- **Hostinger:** https://www.hostinger.com/tutorials/vps
- **This Repo:** https://github.com/snehamehrin22/ai_product_intelligence

---

## 🤝 Support

- GitHub Issues: Report bugs or ask questions
- Check the detailed guides in each folder
- OpenClaw/Claude Code official docs

---

## ✨ What You Get

After completing this setup:

✅ OpenClaw messaging AI accessible from phone
✅ Claude Code terminal AI for development
✅ Secure VPS with firewall + SSL
✅ Regular user account for safe development
✅ Git workflow for project management
✅ Automated backups
✅ tmux for persistent sessions

**Ready to start?** Pick your first tool and follow the quickstart guide!

---

**Version:** 1.0
**Last Updated:** 2026-02-07
**For:** Hostinger VPS (Ubuntu 22.04/24.04)

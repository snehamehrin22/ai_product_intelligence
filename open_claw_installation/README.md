# OpenClaw & Claude Code VPS Installation Guide

Complete documentation for setting up OpenClaw (messaging AI) and Claude Code (terminal AI) on a Hostinger VPS.

## Quick Navigation

### 🚀 Getting Started

**New to this setup?** Start here:
1. [Quick Start](#quick-start)
2. Choose your path: [OpenClaw](#openclaw-setup) or [Claude Code](#claude-code-setup)
3. [Security Hardening](#security)

### 📚 Documentation Index

#### OpenClaw (Messaging AI Assistant)
- **[QUICK_START.md](QUICK_START.md)** - Get OpenClaw running in 10 minutes
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Complete installation guide (400+ lines)
- **[open_claw_research.md](open_claw_research.md)** - Technology research and analysis
- **[install_openclaw.sh](install_openclaw.sh)** - Automated installation script

#### Claude Code (Terminal AI Assistant)
- **[CLAUDE_CODE_QUICKSTART.md](CLAUDE_CODE_QUICKSTART.md)** - Get Claude Code running in 5 minutes
- **[CLAUDE_CODE_INSTALLATION.md](CLAUDE_CODE_INSTALLATION.md)** - Complete guide with authentication
- **[install_claude_code.sh](install_claude_code.sh)** - Automated installation script

#### Security
- **[SECURITY_GUIDE.md](SECURITY_GUIDE.md)** - Complete security hardening guide
- **[security_hardening.sh](security_hardening.sh)** - Automated security setup

#### User Setup (Multi-User Environment)
- **[USER_QUICK_START.md](USER_QUICK_START.md)** - Setup user account in 10 minutes
- **[USER_SETUP_GUIDE.md](USER_SETUP_GUIDE.md)** - Complete user setup with Git
- **[setup_user_account.sh](setup_user_account.sh)** - Automated user setup script

#### Configuration
- **[.env.example](.env.example)** - Environment variables template

---

## Quick Start

### What Do You Want to Set Up?

#### Option A: OpenClaw (Messaging AI)
**What it is:** AI assistant accessible via WhatsApp, Telegram, Discord, etc.
**Time:** 10-20 minutes
**Start here:** [QUICK_START.md](QUICK_START.md)

```bash
# Automated installation
chmod +x install_openclaw.sh
./install_openclaw.sh
```

#### Option B: Claude Code (Terminal AI)
**What it is:** AI coding assistant in your terminal
**Time:** 5-10 minutes
**Start here:** [CLAUDE_CODE_QUICKSTART.md](CLAUDE_CODE_QUICKSTART.md)

```bash
# Automated installation
chmod +x install_claude_code.sh
./install_claude_code.sh
```

#### Option C: Both (Recommended)
**What you get:** Best of both worlds - messaging AI + terminal AI
**Time:** 30 minutes
**Both can run on the same VPS!**

1. Install OpenClaw first (see Option A)
2. Then install Claude Code (see Option B)
3. Secure your setup (see Security section)

---

## System Requirements

### Minimum VPS Specs
- **CPU:** 2 vCPU
- **RAM:** 4GB
- **Storage:** 20GB SSD
- **OS:** Ubuntu 22.04 or 24.04 LTS

### Recommended Hostinger Plan
- **KVM 1:** 2 vCPU, 4GB RAM, 50GB SSD ($6-8/mo)
- **KVM 2:** 4 vCPU, 8GB RAM, 100GB SSD (for heavy usage)

### Prerequisites
- SSH access to VPS
- Root or sudo privileges
- At least ONE of:
  - Anthropic API key (for OpenClaw)
  - OpenAI API key (for OpenClaw)
  - Claude Pro/Max subscription (for Claude Code)
  - Google Gemini API key (free tier available)

---

## OpenClaw Setup

### What is OpenClaw?
Personal AI assistant accessible through messaging platforms:
- WhatsApp, Telegram, Discord, Slack, Signal, iMessage
- Self-hosted on your VPS
- Supports multiple AI providers
- 50+ integrations

### Installation Methods

**Method 1: Hostinger One-Click (Easiest)**
1. hPanel → VPS → Docker Manager → Catalog
2. Search "OpenClaw" → Deploy
3. Add API keys
4. Access dashboard: `http://VPS_IP:18789`

**Method 2: Automated Script**
```bash
chmod +x install_openclaw.sh
./install_openclaw.sh
```

**Time:** 10-20 minutes
**Full guide:** [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

---

## Claude Code Setup

### What is Claude Code?
AI coding assistant in your terminal:
- Natural language commands
- File operations, code generation
- Project-wide analysis
- Persistent conversation threads

### Installation

```bash
# Install
curl -fsSL https://claude.ai/install.sh | bash
source ~/.bashrc

# Authenticate (requires SSH port forwarding)
claude /login

# Start using
claude "hello"
```

**Time:** 5-10 minutes
**Full guide:** [CLAUDE_CODE_INSTALLATION.md](CLAUDE_CODE_INSTALLATION.md)

### Authentication Note
Claude Code requires SSH port forwarding for authentication on VPS.
See [CLAUDE_CODE_INSTALLATION.md](CLAUDE_CODE_INSTALLATION.md#authentication-setup-headless-environment) for details.

---

## Security

### Essential Security Steps

**After installation, secure your VPS:**

```bash
# Run security hardening script
chmod +x security_hardening.sh
./security_hardening.sh
```

**What it does:**
- ✅ Configures UFW firewall
- ✅ Installs Fail2Ban
- ✅ Enables automatic updates
- ✅ Sets up daily backups
- ✅ Hardens SSH (optional)

**Manual setup:** [SECURITY_GUIDE.md](SECURITY_GUIDE.md)

### Quick Security Checklist
- [ ] Firewall configured (UFW)
- [ ] SSL/HTTPS set up (with domain)
- [ ] SSH hardened (key-based auth)
- [ ] Automatic updates enabled
- [ ] Backups automated
- [ ] Fail2Ban protecting SSH

---

## Multi-User Setup

### Running as Regular User (Recommended)

**Why use a regular user account?**
- Safer for daily development
- Better Git workflow
- Separates system admin from development

**Setup Steps:**

```bash
# As root
chmod +x setup_user_account.sh
./setup_user_account.sh

# As your user
ssh yourname@VPS_IP
curl -fsSL https://claude.ai/install.sh | bash
cd ~/projects/ai_product_intelligence
```

**Full guide:** [USER_SETUP_GUIDE.md](USER_SETUP_GUIDE.md)

---

## Architecture Overview

### How Everything Works Together

```
┌─────────────────────────────────────┐
│         Your Hostinger VPS          │
│                                     │
│  ┌────────────────────────────────┐ │
│  │ OpenClaw (Docker)              │ │
│  │ - Port 18789 (localhost only)  │ │
│  │ - Nginx reverse proxy          │ │
│  │ - Accessed via HTTPS           │ │
│  └────────────────────────────────┘ │
│                                     │
│  ┌────────────────────────────────┐ │
│  │ Claude Code (Terminal)         │ │
│  │ - Runs in tmux sessions        │ │
│  │ - Accessed via SSH             │ │
│  │ - No network ports needed      │ │
│  └────────────────────────────────┘ │
│                                     │
│  ┌────────────────────────────────┐ │
│  │ Security                       │ │
│  │ - UFW Firewall                 │ │
│  │ - Fail2Ban                     │ │
│  │ - SSL/HTTPS                    │ │
│  │ - Automated Backups            │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Resource Usage
- OpenClaw: ~500MB-1GB RAM (always running)
- Claude Code: ~500MB RAM (on-demand)
- **Total:** Fits comfortably in 4GB VPS

---

## Cost Breakdown

### VPS Hosting
- Hostinger KVM 1: ~$6-8/month
- Hostinger KVM 2: ~$12-15/month

### AI API Costs (Pay-per-use)
- **OpenClaw:**
  - Anthropic Claude: ~$3 per 1M tokens
  - OpenAI GPT-4o: ~$2.50 per 1M tokens
  - **Google Gemini: FREE tier available**
- **Claude Code:**
  - Included with Claude Pro/Max ($20-30/mo)

### Typical Monthly Total
- **Minimum:** $10-15 (VPS + free Gemini for OpenClaw)
- **Typical:** $20-30 (VPS + Claude subscription)
- **Heavy use:** $50-100 (VPS + multiple API services)

---

## Troubleshooting

### Common Issues

**OpenClaw:**
- Can't access dashboard → Check firewall: `sudo ufw allow 18789/tcp`
- API errors → Verify API keys in docker-compose.yml
- Container not running → `cd /opt/openclaw && docker compose ps`

**Claude Code:**
- Command not found → `export PATH="$HOME/.local/bin:$PATH"`
- Authentication fails → Use SSH port forwarding method
- Session lost → Use tmux for persistent sessions

**Git/GitHub:**
- Permission denied → Check SSH keys: `ssh -T git@github.com`
- Can't push → Verify remote: `git remote -v`

**See full troubleshooting:**
- OpenClaw: [INSTALLATION_GUIDE.md#troubleshooting](INSTALLATION_GUIDE.md#troubleshooting)
- Claude Code: [CLAUDE_CODE_INSTALLATION.md#troubleshooting](CLAUDE_CODE_INSTALLATION.md#troubleshooting)

---

## File Structure

```
open_claw_installation/
├── README.md                          # This file
│
├── OpenClaw Documentation
│   ├── QUICK_START.md                 # Fast setup
│   ├── INSTALLATION_GUIDE.md          # Complete guide
│   ├── open_claw_research.md          # Research notes
│   ├── install_openclaw.sh            # Auto-installer
│   └── .env.example                   # Config template
│
├── Claude Code Documentation
│   ├── CLAUDE_CODE_QUICKSTART.md      # Fast setup
│   ├── CLAUDE_CODE_INSTALLATION.md    # Complete guide
│   └── install_claude_code.sh         # Auto-installer
│
├── Security
│   ├── SECURITY_GUIDE.md              # Security manual
│   └── security_hardening.sh          # Auto-setup
│
└── User Setup
    ├── USER_QUICK_START.md            # Fast setup
    ├── USER_SETUP_GUIDE.md            # Complete guide
    └── setup_user_account.sh          # Auto-setup
```

---

## Quick Reference

### OpenClaw
```bash
cd /opt/openclaw
docker compose ps          # Check status
docker compose logs -f     # View logs
docker compose restart     # Restart
```

### Claude Code
```bash
claude                     # Start interactive
claude "query"             # One-off command
claude /login              # Authenticate
```

### tmux
```bash
tmux new -s claude         # Create session
Ctrl+B then D              # Detach
tmux attach -t claude      # Reattach
```

### Git
```bash
git pull                   # Get latest
git add .                  # Stage changes
git commit -m "message"    # Commit
git push                   # Push to GitHub
```

---

## Support & Resources

### Official Documentation
- OpenClaw: https://docs.openclaw.ai/
- Claude Code: https://code.claude.com/docs/
- Hostinger: https://www.hostinger.com/tutorials/vps

### This Repository
- GitHub: https://github.com/snehamehrin22/ai_product_intelligence
- Issues: Report problems or ask questions via GitHub Issues

### Community
- Check official websites for Discord/forum links
- GitHub Discussions for this repository

---

## Next Steps

### After Installation

1. **Secure your VPS**
   - Run `security_hardening.sh`
   - Set up SSL with domain
   - Configure backups

2. **Set up user account**
   - Run `setup_user_account.sh`
   - Clone repository as user
   - Install Claude Code for user

3. **Start using**
   - OpenClaw: Connect messaging platforms
   - Claude Code: Start coding with AI
   - Git: Sync your work

4. **Optimize**
   - Monitor resource usage
   - Adjust configurations
   - Set up additional integrations

---

## License

Documentation and scripts in this repository are provided as-is for educational and personal use.

OpenClaw and Claude Code are separate products with their own licenses:
- OpenClaw: MIT License
- Claude Code: Anthropic Terms of Service

---

## Contributing

Found an issue or want to improve this documentation?
1. Fork the repository
2. Make your changes
3. Submit a pull request

---

## Version History

- **v1.0** (2026-02-07) - Initial comprehensive documentation
  - OpenClaw installation guides
  - Claude Code installation guides
  - Security hardening guides
  - User setup guides
  - Automated installation scripts

---

**Need help?** Start with the Quick Start guides, then refer to the comprehensive guides for details.

**Ready to begin?** Choose your path:
- 🔹 OpenClaw: [QUICK_START.md](QUICK_START.md)
- 🔸 Claude Code: [CLAUDE_CODE_QUICKSTART.md](CLAUDE_CODE_QUICKSTART.md)
- 🔐 Security: [SECURITY_GUIDE.md](SECURITY_GUIDE.md)
- 👤 User Setup: [USER_QUICK_START.md](USER_QUICK_START.md)

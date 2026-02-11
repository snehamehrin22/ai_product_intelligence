# Claude Code Quick Start Guide for VPS

## TL;DR - Get Started in 5 Minutes

```bash
# 1. Install
curl -fsSL https://claude.ai/install.sh | bash
source ~/.bashrc

# 2. Authenticate (requires SSH port forwarding)
claude /login
# Follow prompts, use SSH tunnel from local machine

# 3. Start in tmux
tmux new -s claude
claude

# 4. Detach and keep running
Ctrl+B then D
```

---

## Automated Installation

**Easiest way - use the installation script:**

```bash
# Make script executable
chmod +x install_claude_code.sh

# Run
./install_claude_code.sh
```

The script will:
- ✓ Check system requirements
- ✓ Install Claude Code
- ✓ Configure tmux
- ✓ Guide you through authentication
- ✓ Create helper scripts

---

## Manual Installation (Step-by-Step)

### 1. Install Claude Code

```bash
curl -fsSL https://claude.ai/install.sh | bash
source ~/.bashrc
claude --version
```

### 2. Install tmux

```bash
sudo apt update
sudo apt install -y tmux
```

### 3. Configure tmux

```bash
cat > ~/.tmux.conf <<'EOF'
set -g mouse on
set -g history-limit 10000
set -g default-terminal "screen-256color"
bind | split-window -h
bind - split-window -v
EOF

tmux source-file ~/.tmux.conf
```

### 4. Authenticate

**On VPS:**
```bash
claude /login
```

You'll see:
```
To authenticate, please visit:
http://localhost:12345/auth?code=abc123...
```

**On your LOCAL machine (not VPS):**
```bash
# Replace 12345 with actual port from above
ssh -L 12345:localhost:12345 root@YOUR_VPS_IP
```

**In your LOCAL browser:**
- Open the URL shown by `claude /login`
- Log in to Claude
- Authorize

**Back on VPS:**
- Authentication completes automatically
- Done!

---

## Essential Commands

### Helper Scripts (Installed Automatically)

```bash
# Start Claude in persistent tmux session
claude-start

# View authentication help
claude-auth-help

# View tmux shortcuts
tmux-help
```

### Claude Code Commands

```bash
# Interactive mode
claude

# One-off command
claude "summarize this project"

# Check health
claude doctor

# Help
claude /help

# Login/re-authenticate
claude /login
```

### tmux Commands

```bash
# Create session
tmux new -s claude

# Detach (keeps running)
Ctrl+B then D

# Attach to session
tmux attach -t claude

# List sessions
tmux ls

# Kill session
tmux kill-session -t claude
```

---

## Authentication Troubleshooting

### Problem: Port Forwarding Doesn't Work

**Solution: Use auth.json transfer method**

**On a computer where Claude Code is already authenticated:**

```bash
# 1. Copy auth file content
cat ~/.config/claude-code/auth.json

# 2. On VPS, create the file
mkdir -p ~/.config/claude-code
nano ~/.config/claude-code/auth.json
# Paste the content, save

# 3. Set permissions
chmod 600 ~/.config/claude-code/auth.json

# 4. Test
claude "hello"
```

### Problem: Authentication Expires

**Solution: Re-authenticate**

```bash
rm ~/.config/claude-code/auth.json
claude /login
# Follow port forwarding steps again
```

---

## Typical Workflow

### Starting Your Day

```bash
# SSH into VPS
ssh root@YOUR_VPS_IP

# Attach to Claude session (or create if doesn't exist)
tmux attach -t claude || tmux new -s claude
claude

# Now you're in Claude Code
```

### Working with Claude

```bash
# Inside Claude interactive mode:

# Create a new thread
/thread new "Build a Python web scraper"

# Ask Claude to help
> "Create a script that scrapes Hacker News top stories"

# Claude generates code
# Review and request changes
> "Add error handling and save to JSON"

# Exit when done
/exit
```

### Ending Your Day

```bash
# Detach from tmux (Claude keeps running)
Ctrl+B then D

# Disconnect from VPS
exit
```

### Next Day

```bash
# SSH back in
ssh root@YOUR_VPS_IP

# Reattach to same Claude session
tmux attach -t claude

# Your conversation history is still there!
```

---

## Common Use Cases

### 1. Code Review

```bash
claude "review the code in app.py and suggest improvements"
```

### 2. Generate Code

```bash
claude "create a Python script that monitors disk usage"
```

### 3. Debug

```bash
claude "why is nginx returning 502 error?"
```

### 4. Manage OpenClaw

```bash
claude "check OpenClaw container logs for errors"
claude "update OpenClaw to latest version"
```

### 5. System Administration

```bash
claude "create a backup script for my database"
claude "why is my VPS using so much memory?"
```

---

## Integration with OpenClaw

Both run on same VPS:

```bash
# Check what's running
docker compose ps  # OpenClaw
tmux ls           # Claude sessions

# Resource usage
htop              # Overall
docker stats      # OpenClaw specifically
```

**Recommended approach:**
- OpenClaw: Always running (Docker daemon)
- Claude Code: On-demand (tmux session)

---

## Resource Management

### Check Memory

```bash
free -h
```

### If Running Low

```bash
# Stop Claude Code when not in use
tmux kill-session -t claude

# Restart OpenClaw if needed
cd /opt/openclaw
docker compose restart
```

---

## Quick Reference Card

```
╔═══════════════════════════════════════════════════════════╗
║                  CLAUDE CODE CHEAT SHEET                  ║
╠═══════════════════════════════════════════════════════════╣
║ Installation:                                             ║
║   curl -fsSL https://claude.ai/install.sh | bash          ║
║                                                            ║
║ Start Claude:                                              ║
║   claude-start         (in tmux)                           ║
║   claude              (direct)                             ║
║                                                            ║
║ Authentication:                                            ║
║   claude /login                                            ║
║   claude-auth-help    (for instructions)                   ║
║                                                            ║
║ tmux Shortcuts:                                            ║
║   Detach:             Ctrl+B then D                        ║
║   Attach:             tmux attach -t claude                ║
║   List:               tmux ls                              ║
║                                                            ║
║ Claude Commands:                                           ║
║   /help               Show all commands                    ║
║   /thread new         Create conversation                  ║
║   /thread list        View all threads                     ║
║   /exit               Quit Claude                          ║
║                                                            ║
║ Health Check:                                              ║
║   claude doctor                                            ║
╚═══════════════════════════════════════════════════════════╝
```

---

## Troubleshooting

### "command not found: claude"

```bash
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc
```

### "authentication required"

```bash
claude /login
# Or transfer auth.json from local machine
```

### "out of memory"

```bash
# Check usage
free -h

# Close Claude when not in use
tmux kill-session -t claude
```

### tmux session disappeared

```bash
# Sessions don't survive reboots
# Create new session
tmux new -s claude
```

---

## Next Steps

1. **Read full guide:** `CLAUDE_CODE_INSTALLATION.md`
2. **Explore features:** Try different types of queries
3. **Optimize workflow:** Create custom aliases
4. **Learn tmux:** Master session management

---

## Getting Help

- Full documentation: `CLAUDE_CODE_INSTALLATION.md`
- Authentication help: `claude-auth-help`
- tmux help: `tmux-help`
- Claude help: `claude /help`
- Official docs: https://code.claude.com/docs/

---

**Installation Time:** 5-10 minutes
**Learning Curve:** Easy
**Prerequisites:** Claude subscription

**Now you have AI-powered coding assistance on your VPS!** 🎉

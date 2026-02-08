# Claude Code Installation Guide for Hostinger VPS

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation Methods](#installation-methods)
4. [Authentication Setup (Headless Environment)](#authentication-setup-headless-environment)
5. [Session Persistence with tmux](#session-persistence-with-tmux)
6. [Basic Usage](#basic-usage)
7. [Integration with OpenClaw](#integration-with-openclaw)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Configuration](#advanced-configuration)

---

## Overview

**Claude Code** is Anthropic's official CLI tool that brings Claude AI assistance directly to your terminal. This guide covers installation on a Hostinger VPS where you already have OpenClaw running.

**What is Claude Code?**
- AI-powered coding assistant in your terminal
- Can read/write files, run commands, search codebases
- Persistent conversation threads
- Works with your existing development workflow

**Key Features:**
- Natural language commands
- File and directory operations
- Code generation and refactoring
- Project-wide search and analysis
- Multi-threaded conversations

---

## Prerequisites

### System Requirements

**Minimum:**
- 4GB RAM (you already have this from OpenClaw setup)
- Ubuntu 20.04+ (your VPS meets this)
- Internet connection
- Bash or Zsh shell

**Recommended:**
- 8GB+ RAM for heavy usage
- SSD storage
- Stable network connection

### Account Requirements

**You need ONE of the following:**
1. **Claude Pro or Claude Max** subscription ($20-30/month)
2. **Claude Console** account with active billing
3. **Claude for Teams/Enterprise** access
4. **Cloud provider integration** (AWS Bedrock, Google Vertex AI, etc.)

**Check your access:**
- Visit https://console.anthropic.com/
- Ensure you have active billing or subscription

### VPS Access

You should already have:
- ✅ SSH access to your Hostinger VPS
- ✅ Root or sudo privileges
- ✅ Firewall configured (from OpenClaw security setup)

---

## Installation Methods

### Method 1: Native Install (Recommended)

**Fastest and cleanest method - no Node.js required**

**Step 1: SSH into your VPS**
```bash
ssh root@YOUR_VPS_IP
# Or use your configured SSH user
```

**Step 2: Run the installer**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**What this does:**
- Downloads latest Claude Code binary
- Installs to `~/.local/bin/claude`
- Updates PATH automatically
- Enables auto-updates

**Step 3: Reload shell configuration**
```bash
source ~/.bashrc
# or
source ~/.profile
```

**Step 4: Verify installation**
```bash
claude --version
```

**Expected output:**
```
claude version 0.x.x
```

**If command not found:**
```bash
# Add to PATH manually
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Method 2: Manual Binary Install

**If installer fails or you want more control:**

```bash
# Download latest release
wget https://github.com/anthropics/claude-code/releases/latest/download/claude-linux-x64 -O ~/.local/bin/claude

# Make executable
chmod +x ~/.local/bin/claude

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
claude --version
```

### Method 3: npm Install (Deprecated but Works)

**Only if you need a specific version:**

```bash
# Install Node.js if not present
sudo apt update
sudo apt install -y nodejs npm

# Install Claude Code globally
npm install -g @anthropic-ai/claude-code

# Verify
claude --version
```

**Note:** npm method is deprecated and may not receive updates.

---

## Authentication Setup (Headless Environment)

The main challenge: Claude Code authentication requires opening a browser, but your VPS is headless (no GUI).

### Solution 1: SSH Port Forwarding (Recommended)

**This method forwards the auth URL from VPS to your local browser**

**Step 1: Start authentication on VPS**
```bash
# On your VPS
claude /login
```

**You'll see output like:**
```
To authenticate, please visit:
http://localhost:12345/auth?code=abc123xyz...

Waiting for authentication...
```

**Copy the URL and note the port (e.g., 12345)**

**Step 2: On your LOCAL machine (not VPS), create SSH tunnel**

**macOS/Linux:**
```bash
ssh -L 12345:localhost:12345 root@YOUR_VPS_IP
```

**Windows (PowerShell):**
```powershell
ssh -L 12345:localhost:12345 root@YOUR_VPS_IP
```

**Step 3: Open the auth URL in your local browser**
- Open `http://localhost:12345/auth?code=abc123xyz...` in Chrome/Firefox
- You'll be redirected to Anthropic's login page
- Log in with your Claude account
- Authorize the CLI

**Step 4: Return to VPS terminal**
- Authentication should complete automatically
- You'll see: "Authentication successful!"

**Done!** Claude Code is now authenticated on your VPS.

### Solution 2: Transfer Credentials (Alternative)

**If you have Claude Code already authenticated on your local machine:**

**Step 1: Locate auth file on local machine**

**macOS/Linux:**
```bash
cat ~/.config/claude-code/auth.json
```

**Windows:**
```powershell
type %USERPROFILE%\.config\claude-code\auth.json
```

**Step 2: Copy to VPS**

**Method A: Direct copy (if auth.json exists):**
```bash
# On local machine
scp ~/.config/claude-code/auth.json root@YOUR_VPS_IP:/tmp/
```

**Method B: Manual copy:**
- Copy the contents of `auth.json`
- Create file on VPS:
```bash
# On VPS
mkdir -p ~/.config/claude-code
nano ~/.config/claude-code/auth.json
# Paste contents, save (Ctrl+O, Enter, Ctrl+X)
```

**Step 3: Set permissions**
```bash
chmod 600 ~/.config/claude-code/auth.json
```

**Step 4: Test**
```bash
claude "hello"
```

### Solution 3: API Key Method (For CI/CD or Automated Use)

**If you have an API key instead:**

```bash
# Set environment variable
export CLAUDE_CODE_API_KEY="your-api-key-here"

# Add to bashrc for persistence
echo 'export CLAUDE_CODE_API_KEY="your-api-key-here"' >> ~/.bashrc
```

**Note:** This method may have limitations vs. full OAuth.

---

## Session Persistence with tmux

**Problem:** SSH connection drops = Claude session lost
**Solution:** tmux keeps sessions running even when disconnected

### Install and Configure tmux

**Step 1: Install tmux**
```bash
sudo apt update
sudo apt install -y tmux
```

**Step 2: Configure tmux**
```bash
# Create config file
nano ~/.tmux.conf
```

**Add this configuration:**
```bash
# Enable mouse support
set -g mouse on

# Increase scrollback buffer
set -g history-limit 10000

# Better colors
set -g default-terminal "screen-256color"

# Start window numbering at 1
set -g base-index 1

# Easy config reload
bind r source-file ~/.tmux.conf \; display "Config reloaded!"

# Split panes using | and -
bind | split-window -h
bind - split-window -v

# Switch panes using Alt+arrow without prefix
bind -n M-Left select-pane -L
bind -n M-Right select-pane -R
bind -n M-Up select-pane -U
bind -n M-Down select-pane -D
```

**Save and exit** (Ctrl+O, Enter, Ctrl+X)

**Step 3: Load configuration**
```bash
tmux source-file ~/.tmux.conf
```

### Using tmux with Claude Code

**Create a Claude session:**
```bash
tmux new -s claude
```

**Inside tmux, start Claude:**
```bash
claude
```

**Detach from session** (keep it running):
```
Ctrl+B then D
```

**Reattach to session:**
```bash
tmux attach -t claude
# or shorthand
tmux a -t claude
```

**List all sessions:**
```bash
tmux ls
```

**Kill a session:**
```bash
tmux kill-session -t claude
```

### tmux Quick Reference

| Action | Command |
|--------|---------|
| Create session | `tmux new -s name` |
| Attach to session | `tmux attach -t name` |
| Detach from session | `Ctrl+B then D` |
| List sessions | `tmux ls` |
| Kill session | `tmux kill-session -t name` |
| Split horizontally | `Ctrl+B then "` |
| Split vertically | `Ctrl+B then %` |
| Switch panes | `Ctrl+B then arrow keys` |
| Scroll mode | `Ctrl+B then [` (q to exit) |

---

## Basic Usage

### Starting Claude Code

**Interactive mode (recommended):**
```bash
claude
```

**One-off command:**
```bash
claude "summarize README.md"
```

### Essential Commands

**Inside Claude Code:**

```bash
# Get help
/help

# Create new conversation thread
/thread new "Let's build a REST API"

# List all threads
/thread list

# Switch to a thread
/thread switch THREAD_ID

# View thread details
/thread view THREAD_ID

# Delete a thread
/thread delete THREAD_ID

# Login/re-authenticate
/login

# Check health
/doctor

# Exit
/exit
# or Ctrl+D
```

### Example Usage

**1. Code review:**
```bash
claude "review the code in src/app.py and suggest improvements"
```

**2. Generate code:**
```bash
claude "create a Python script that monitors disk usage and sends alerts"
```

**3. Debug help:**
```bash
claude "why is my nginx config failing? here's the error: [paste error]"
```

**4. Project analysis:**
```bash
claude "analyze this codebase and explain the architecture"
```

**5. Refactoring:**
```bash
claude "refactor auth.js to use async/await instead of promises"
```

### Working with Files

**Claude Code can:**
- Read files in current directory
- Write/edit files
- Create new files
- Search across multiple files

**Example:**
```bash
claude "read config.yml and create a .env file with the same settings"
```

---

## Integration with OpenClaw

### Running Both on Same VPS

**Good news:** Claude Code and OpenClaw can coexist perfectly!

**Resource considerations:**
- Claude Code: ~500MB RAM when active
- OpenClaw: ~500MB-1GB RAM
- Your 4GB VPS can handle both

**Recommended setup:**

1. **OpenClaw:** Runs in Docker (always on)
   - Port 18789 (localhost only)
   - Accessed via Nginx reverse proxy

2. **Claude Code:** Runs in tmux (on-demand)
   - No ports needed (terminal only)
   - Start when you need AI coding help

**Workflow:**
```bash
# SSH into VPS
ssh root@YOUR_VPS_IP

# Check OpenClaw status
cd /opt/openclaw
docker compose ps

# Start Claude Code in tmux
tmux new -s claude
claude

# Detach and do other work
Ctrl+B then D

# Both running simultaneously!
```

### Using Claude Code to Manage OpenClaw

**Example commands:**

```bash
# Inside Claude Code
claude "check OpenClaw logs for errors"
claude "update OpenClaw docker-compose.yml to use latest image"
claude "create a backup script for OpenClaw configuration"
claude "analyze OpenClaw memory usage and suggest optimizations"
```

### Shared Security Configuration

**Both tools benefit from your existing security setup:**
- ✅ UFW firewall (no new ports needed for Claude Code)
- ✅ Fail2Ban (protects SSH access to both)
- ✅ Automatic updates
- ✅ Backup automation (add Claude Code config to backup)

**Add Claude Code to backup script:**
```bash
# Edit backup script
sudo nano /usr/local/bin/backup-openclaw.sh
```

**Add to backup section:**
```bash
# Backup Claude Code configuration
tar -czf $BACKUP_DIR/claude_code_config_$DATE.tar.gz \
    ~/.config/claude-code \
    ~/.tmux.conf 2>/dev/null
```

---

## Troubleshooting

### Issue 1: Command Not Found

**Symptoms:**
```bash
$ claude
bash: claude: command not found
```

**Solutions:**

1. **Add to PATH:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

2. **Verify installation location:**
```bash
find ~ -name claude -type f 2>/dev/null
```

3. **Reinstall:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

### Issue 2: Authentication Fails

**Symptoms:**
- "Authentication required" errors
- Login URL doesn't work

**Solutions:**

1. **Check subscription status:**
   - Visit https://console.anthropic.com/
   - Verify active billing

2. **Retry with fresh login:**
```bash
rm ~/.config/claude-code/auth.json
claude /login
```

3. **Check firewall on local machine:**
   - Ensure port forwarding isn't blocked
   - Try different port: `ssh -L 54321:localhost:PORT ...`

4. **Transfer credentials from working install:**
   - Copy auth.json from local machine (see Solution 2 above)

### Issue 3: Permission Denied

**Symptoms:**
```bash
Error: EACCES: permission denied
```

**Solutions:**

1. **Fix auth.json permissions:**
```bash
chmod 600 ~/.config/claude-code/auth.json
```

2. **Fix binary permissions:**
```bash
chmod +x ~/.local/bin/claude
```

3. **Check directory ownership:**
```bash
ls -la ~/.config/claude-code
# Should be owned by your user
```

### Issue 4: High Memory Usage

**Symptoms:**
- VPS becomes slow
- Out of memory errors

**Solutions:**

1. **Check memory usage:**
```bash
free -h
htop
```

2. **Limit Claude Code usage:**
   - Close when not in use
   - Don't run multiple instances

3. **Upgrade VPS if needed:**
   - Consider 8GB plan for heavy usage

4. **Monitor both services:**
```bash
docker stats  # OpenClaw
ps aux | grep claude  # Claude Code
```

### Issue 5: tmux Session Lost

**Symptoms:**
- Can't find previous session
- Session disappeared after reboot

**Solutions:**

1. **List sessions:**
```bash
tmux ls
```

2. **Attach to running session:**
```bash
tmux attach -t claude
```

3. **Note:** tmux sessions don't survive server reboots

4. **Auto-start tmux session (optional):**
```bash
# Add to ~/.bashrc
if command -v tmux &> /dev/null && [ -z "$TMUX" ]; then
    tmux attach -t claude || tmux new -s claude
fi
```

### Issue 6: Cannot Read/Write Files

**Symptoms:**
- Claude can't access project files
- Permission errors

**Solutions:**

1. **Run Claude in correct directory:**
```bash
cd /path/to/your/project
claude
```

2. **Check file permissions:**
```bash
ls -la
# Ensure files are readable by your user
```

3. **Grant access if needed:**
```bash
chmod 755 directory/
chmod 644 file.txt
```

---

## Advanced Configuration

### Custom Installation Directory

**Install to custom location:**
```bash
# Download binary
wget https://github.com/anthropics/claude-code/releases/latest/download/claude-linux-x64

# Move to custom location
sudo mv claude-linux-x64 /usr/local/bin/claude
sudo chmod +x /usr/local/bin/claude

# Verify
which claude
claude --version
```

### Multiple User Setup

**If multiple users need Claude Code:**

```bash
# Install globally
sudo mv claude /usr/local/bin/

# Each user runs
claude /login  # Separate auth per user
```

### Disable Auto-Updates

**If you want manual control:**

```bash
# Create config file
mkdir -p ~/.config/claude-code
nano ~/.config/claude-code/config.json
```

**Add:**
```json
{
  "autoUpdate": false
}
```

### Update Claude Code Manually

```bash
# Check for updates
claude update

# Or reinstall latest
curl -fsSL https://claude.ai/install.sh | bash
```

### Configure Default Model

**If you have access to multiple models:**

```bash
# Set preferred model
claude config set model claude-sonnet-4.5

# View current config
claude config show
```

### Logging and Debug Mode

**Enable verbose logging:**
```bash
# Run with debug output
CLAUDE_DEBUG=1 claude

# Save logs to file
claude 2>&1 | tee claude.log
```

### Resource Limits

**Limit Claude Code resource usage:**

```bash
# Limit memory (systemd)
systemd-run --user --scope -p MemoryLimit=1G claude

# Or use ulimit
ulimit -v 1048576  # 1GB in KB
claude
```

---

## Best Practices

### 1. Use tmux Always

**Never run Claude Code without tmux on a VPS:**
- Prevents losing work on disconnect
- Allows background operation
- Enables easy session resumption

### 2. Organize Projects

**Create dedicated directories:**
```bash
mkdir -p ~/projects/{openclaw,webapp,scripts}
cd ~/projects/openclaw
claude  # Start in project context
```

### 3. Security

**Protect credentials:**
```bash
# Ensure auth file is private
chmod 600 ~/.config/claude-code/auth.json

# Never share auth.json
# Never commit to git
```

### 4. Resource Management

**Monitor usage:**
```bash
# Before starting Claude
free -h
df -h

# During usage
htop
```

**Close when done:**
```bash
# Exit Claude properly
/exit

# Kill tmux session if not needed
tmux kill-session -t claude
```

### 5. Regular Backups

**Include Claude config in backups:**
```bash
# Add to your backup routine
tar -czf claude_backup.tar.gz ~/.config/claude-code ~/.tmux.conf
```

---

## Uninstallation (If Needed)

### Remove Claude Code

**Native install:**
```bash
rm ~/.local/bin/claude
rm -rf ~/.config/claude-code
```

**npm install:**
```bash
npm uninstall -g @anthropic-ai/claude-code
rm -rf ~/.config/claude-code
```

**Remove from PATH:**
```bash
# Edit ~/.bashrc and remove the PATH line
nano ~/.bashrc
source ~/.bashrc
```

---

## Quick Reference

### Essential Commands

```bash
# Installation
curl -fsSL https://claude.ai/install.sh | bash

# Authentication
claude /login

# Start interactive session
claude

# One-off command
claude "your query here"

# Check health
claude doctor

# Version check
claude --version

# Update
claude update
```

### tmux Essentials

```bash
# Create session
tmux new -s claude

# Detach
Ctrl+B then D

# Attach
tmux attach -t claude

# List sessions
tmux ls
```

### Integration

```bash
# Check both services
docker compose ps  # OpenClaw
tmux ls           # Claude sessions

# Monitor resources
htop
docker stats
```

---

## Support and Resources

### Official Documentation
- Main docs: https://code.claude.com/docs/
- GitHub: https://github.com/anthropics/claude-code
- Console: https://console.anthropic.com/

### Community
- GitHub Issues: Bug reports and feature requests
- Anthropic Discord: Community support (check website for invite)

### Hostinger Resources
- VPS Guide: https://www.hostinger.com/tutorials/vps
- Claude Code on Hostinger: https://www.hostinger.com/support/11929523-installing-claude-code-on-a-vps-at-hostinger/

---

## Next Steps

After installation:

1. **Test basic functionality:**
```bash
claude "hello, introduce yourself"
```

2. **Create your first project:**
```bash
mkdir ~/my-project
cd ~/my-project
claude "help me set up a Python project structure"
```

3. **Explore features:**
   - Thread management
   - File operations
   - Code generation
   - Project analysis

4. **Integrate with workflow:**
   - Use for OpenClaw management
   - Automate common tasks
   - Code review and debugging

5. **Monitor and optimize:**
   - Watch resource usage
   - Adjust tmux config
   - Refine prompts for better results

---

**Installation Time:** 10-20 minutes
**Difficulty:** Moderate (headless auth is tricky)
**Cost:** Included with Claude subscription

**You now have both OpenClaw (messaging AI) and Claude Code (terminal AI) on your VPS!**

For detailed OpenClaw docs, see: `INSTALLATION_GUIDE.md`
For security hardening, see: `SECURITY_GUIDE.md`

---

**Document Version:** 1.0
**Last Updated:** 2026-02-07
**For:** Hostinger VPS with existing OpenClaw installation

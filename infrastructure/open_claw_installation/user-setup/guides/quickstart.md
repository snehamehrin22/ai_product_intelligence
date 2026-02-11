# User Account Quick Start

## TL;DR - Setup in 10 Minutes

### As Root (on VPS)

```bash
# 1. Run the setup script
chmod +x setup_user_account.sh
./setup_user_account.sh

# Follow prompts to:
# - Create username
# - Set password
# - Configure Git
# - Set up GitHub SSH key
# - Clone repository
```

### As Your User (after setup)

```bash
# 1. SSH as your user
ssh yourname@YOUR_VPS_IP

# 2. Install Claude Code
curl -fsSL https://claude.ai/install.sh | bash
source ~/.bashrc

# 3. Authenticate Claude
claude /login
# Use SSH port forwarding from local machine

# 4. Install tmux
sudo apt install -y tmux

# 5. Start working!
cd ~/projects/ai_product_intelligence/open_claw_installation
tmux new -s claude
claude
```

---

## Daily Workflow

### Start Work

```bash
# SSH to VPS
ssh yourname@YOUR_VPS_IP

# Navigate to project
cd ~/projects/ai_product_intelligence

# Pull latest changes
git pull

# Start Claude in tmux
tmux new -s claude
claude

# Work...
```

### End Work

```bash
# Commit changes
git add .
git commit -m "Description of work done"
git push

# Detach tmux (Claude keeps running)
Ctrl+B then D

# Disconnect
exit
```

### Resume Work

```bash
# SSH back in
ssh yourname@YOUR_VPS_IP

# Reattach to Claude session
tmux attach -t claude

# Pull any new changes
cd ~/projects/ai_product_intelligence
git pull
```

---

## Essential Commands

### Git
```bash
git pull          # Get latest
git status        # Check changes
git add .         # Stage all
git commit -m ""  # Commit
git push          # Push to GitHub
```

### Claude Code
```bash
claude                       # Start
claude "query"               # One-off
claude /login                # Authenticate
```

### tmux
```bash
tmux new -s claude           # Create
Ctrl+B then D                # Detach
tmux attach -t claude        # Reattach
tmux ls                      # List
```

### Sudo
```bash
sudo docker ps               # Check OpenClaw
sudo systemctl status nginx  # Check nginx
```

---

## Troubleshooting

### Can't SSH as User
```bash
# As root, copy SSH keys
mkdir -p /home/yourname/.ssh
cp ~/.ssh/authorized_keys /home/yourname/.ssh/
chown -R yourname:yourname /home/yourname/.ssh
chmod 700 /home/yourname/.ssh
chmod 600 /home/yourname/.ssh/authorized_keys
```

### Git Push Fails
```bash
# Test GitHub connection
ssh -T git@github.com

# Re-add SSH key if needed
cat ~/.ssh/id_ed25519_github.pub
# Add to github.com/settings/keys
```

### Claude Not Found
```bash
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## Full Documentation

- Complete guide: `USER_SETUP_GUIDE.md`
- Claude Code: `CLAUDE_CODE_INSTALLATION.md`
- OpenClaw: `INSTALLATION_GUIDE.md`
- Security: `SECURITY_GUIDE.md`

---

**Setup Time:** 10-15 minutes
**What You Get:** Full development environment with Git and AI assistance

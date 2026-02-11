# User Setup Guide: Claude Code for Regular User Account

## Overview

This guide helps you set up Claude Code in your regular user account on the VPS, separate from the root installation. You'll also set up Git to sync your projects.

**Current Setup:**
- OpenClaw: Running as root in Docker
- Claude Code (root): Installed but we want user-level access

**Goal:**
- Regular user account with sudo access
- Git configured and repository cloned
- Claude Code installed for regular user
- Ability to work on projects via Git

---

## Step-by-Step Setup

### Phase 1: Create Regular User (Run as Root)

**1. SSH into VPS as root:**
```bash
ssh root@YOUR_VPS_IP
```

**2. Create a new user (if you don't have one):**
```bash
# Replace 'yourname' with your desired username
adduser yourname
```

You'll be prompted for:
- Password (choose a strong one)
- Full name (optional)
- Other info (can skip)

**3. Add user to sudo group:**
```bash
usermod -aG sudo yourname
```

**4. Verify sudo access:**
```bash
# Switch to the user
su - yourname

# Test sudo
sudo whoami
# Should output: root

# Exit back to root
exit
```

### Phase 2: Set Up SSH Access for User

**Option A: Copy Root's SSH Key (Easiest)**

```bash
# As root, copy SSH directory to user
mkdir -p /home/yourname/.ssh
cp ~/.ssh/authorized_keys /home/yourname/.ssh/
chown -R yourname:yourname /home/yourname/.ssh
chmod 700 /home/yourname/.ssh
chmod 600 /home/yourname/.ssh/authorized_keys
```

**Option B: Add New SSH Key**

On your **local machine**:
```bash
# Generate new key pair (if needed)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy to VPS user
ssh-copy-id yourname@YOUR_VPS_IP
```

**Test SSH access as user:**
```bash
# From your local machine
ssh yourname@YOUR_VPS_IP

# Should log in without asking for password (if using keys)
```

---

### Phase 3: Install Git and Configure (As Regular User)

**1. SSH as your regular user:**
```bash
ssh yourname@YOUR_VPS_IP
```

**2. Install Git:**
```bash
sudo apt update
sudo apt install -y git
```

**3. Configure Git identity:**
```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

**4. Verify configuration:**
```bash
git config --list
```

---

### Phase 4: Set Up GitHub SSH Access

**1. Generate SSH key for GitHub:**
```bash
ssh-keygen -t ed25519 -C "your@email.com" -f ~/.ssh/id_ed25519_github
```

Press Enter for no passphrase (or add one for extra security).

**2. Display public key:**
```bash
cat ~/.ssh/id_ed25519_github.pub
```

**3. Add to GitHub:**
- Copy the entire output
- Go to https://github.com/settings/keys
- Click "New SSH key"
- Title: "VPS User Account"
- Paste the key
- Click "Add SSH key"

**4. Create SSH config:**
```bash
nano ~/.ssh/config
```

Add:
```
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_github
  IdentitiesOnly yes
```

Save and exit (Ctrl+O, Enter, Ctrl+X)

**5. Set permissions:**
```bash
chmod 600 ~/.ssh/config
```

**6. Test GitHub connection:**
```bash
ssh -T git@github.com
```

Should see: "Hi snehamehrin22! You've successfully authenticated..."

---

### Phase 5: Clone Your Repository

**1. Create projects directory:**
```bash
mkdir -p ~/projects
cd ~/projects
```

**2. Clone repository:**
```bash
git clone git@github.com:snehamehrin22/ai_product_intelligence.git
```

**3. Navigate to project:**
```bash
cd ai_product_intelligence/open_claw_installation
ls -la
```

You should see all your documentation files!

---

### Phase 6: Install Claude Code (As Regular User)

**1. Install Claude Code:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**2. Update PATH:**
```bash
source ~/.bashrc
```

**3. Verify installation:**
```bash
claude --version
```

Should show: `2.1.34 (Claude Code)` or similar

---

### Phase 7: Authenticate Claude Code

**1. Start authentication:**
```bash
claude /login
```

**2. Copy the URL shown** (e.g., `http://localhost:PORT/auth?code=...`)

**3. On your LOCAL machine, create SSH tunnel:**
```bash
# Replace PORT with actual port number
# Replace yourname with your username
ssh -L PORT:localhost:PORT yourname@YOUR_VPS_IP
```

**4. In your LOCAL browser:**
- Open the copied URL
- Log in with Claude Pro/Max account
- Authorize

**5. Back on VPS:**
- Authentication should complete
- You'll see "Authentication successful!"

---

### Phase 8: Install tmux for Persistent Sessions

**1. Install tmux:**
```bash
sudo apt install -y tmux
```

**2. Create tmux configuration:**
```bash
cat > ~/.tmux.conf <<'EOF'
# Mouse support
set -g mouse on

# Scrollback buffer
set -g history-limit 10000

# Better colors
set -g default-terminal "screen-256color"

# Start numbering at 1
set -g base-index 1

# Split panes shortcuts
bind | split-window -h
bind - split-window -v

# Reload config
bind r source-file ~/.tmux.conf \; display "Config reloaded!"
EOF
```

**3. Load configuration:**
```bash
tmux source-file ~/.tmux.conf
```

---

### Phase 9: Test Your Setup

**1. Test Git workflow:**
```bash
cd ~/projects/ai_product_intelligence
git pull
git status
```

**2. Create a test file:**
```bash
echo "# Test from user account" > test.txt
git add test.txt
git commit -m "Test commit from user account"
git push
```

**3. Test Claude Code:**
```bash
# Start in tmux
tmux new -s claude
claude "hello, introduce yourself"

# Detach
Ctrl+B then D

# Reattach
tmux attach -t claude
```

**4. Verify sudo access:**
```bash
sudo docker ps
# Should show OpenClaw containers
```

---

## Workflow: Working with Projects

### Starting a Work Session

```bash
# 1. SSH to VPS
ssh yourname@YOUR_VPS_IP

# 2. Navigate to project
cd ~/projects/ai_product_intelligence/open_claw_installation

# 3. Pull latest changes
git pull

# 4. Start Claude in tmux
tmux new -s claude
claude

# Work with Claude...

# 5. Detach when done
Ctrl+B then D
```

### Ending a Work Session

```bash
# 1. Commit your changes
git add .
git commit -m "Description of changes"
git push

# 2. Exit (tmux session stays running)
exit
```

### Resuming Work

```bash
# SSH back in
ssh yourname@YOUR_VPS_IP

# Reattach to Claude session
tmux attach -t claude

# Pull any remote changes
cd ~/projects/ai_product_intelligence
git pull
```

---

## Quick Reference

### Essential Commands

**Git:**
```bash
git pull                     # Get latest from GitHub
git status                   # Check changes
git add .                    # Stage all changes
git commit -m "message"      # Commit
git push                     # Push to GitHub
```

**Claude Code:**
```bash
claude                       # Start interactive
claude "query"               # One-off command
claude /login                # Authenticate
```

**tmux:**
```bash
tmux new -s claude           # Create session
Ctrl+B then D                # Detach
tmux attach -t claude        # Reattach
tmux ls                      # List sessions
```

**Sudo:**
```bash
sudo <command>               # Run as root
sudo docker ps               # Check OpenClaw
sudo systemctl status nginx  # Check nginx
```

---

## File Locations

### As Root
```
/opt/openclaw/              # OpenClaw installation
/root/.local/bin/claude     # Root's Claude Code
/root/.openclaw/            # OpenClaw config
```

### As Regular User
```
/home/yourname/projects/ai_product_intelligence/  # Your project
/home/yourname/.local/bin/claude                  # User's Claude Code
/home/yourname/.config/claude-code/               # Claude config
/home/yourname/.ssh/                              # SSH keys
```

---

## Troubleshooting

### Can't SSH as User

**Check SSH service:**
```bash
# As root
systemctl status sshd
```

**Check user exists:**
```bash
# As root
id yourname
```

**Check SSH keys:**
```bash
# As user
ls -la ~/.ssh/
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### Git Push Permission Denied

**Check SSH key:**
```bash
ssh -T git@github.com
```

**Check SSH config:**
```bash
cat ~/.ssh/config
```

**Re-add key to GitHub:**
```bash
cat ~/.ssh/id_ed25519_github.pub
# Copy and add to github.com/settings/keys
```

### Claude Command Not Found

**Add to PATH:**
```bash
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Sudo Asks for Password Every Time

**Extend sudo timeout (optional):**
```bash
# As root
echo "Defaults:yourname timestamp_timeout=30" >> /etc/sudoers.d/yourname
```

---

## Security Best Practices

1. **Use Strong Passwords**
   - For user account
   - For sudo access

2. **SSH Keys Instead of Passwords**
   - Disable password authentication (advanced)
   - Use different keys for different purposes

3. **Don't Share Credentials**
   - Keep auth tokens private
   - Don't commit secrets to Git

4. **Regular Updates**
   ```bash
   sudo apt update && sudo apt upgrade
   ```

5. **Monitor Activity**
   ```bash
   # Check who's logged in
   who

   # Check last logins
   last

   # Check sudo usage
   sudo grep sudo /var/log/auth.log
   ```

---

## Multi-User Benefits

### Root Account
- Manages OpenClaw (Docker)
- System administration
- Security updates
- Firewall configuration

### Regular User Account
- Development work with Claude Code
- Git repository management
- Personal projects
- Safer for daily operations

### Best Practices
- Use regular user for daily work
- Use `sudo` only when needed
- Keep both accounts' Claude Code authenticated
- Sync work via Git

---

## Next Steps

After setup:

1. **Familiarize yourself with the workflow**
   - Practice Git pull/push
   - Use Claude Code in tmux
   - Test sudo access

2. **Customize your environment**
   - Add aliases to `~/.bashrc`
   - Configure your preferred shell
   - Set up additional tools

3. **Start working on projects**
   - Use Claude Code for development
   - Commit frequently
   - Push to GitHub for backup

---

## Quick Setup Script

See `setup_user_account.sh` for automated setup of all the above steps!

---

**Setup Time:** 15-20 minutes
**Difficulty:** Moderate
**Prerequisites:** Root access, GitHub account, Claude subscription

For detailed OpenClaw docs: `INSTALLATION_GUIDE.md`
For Claude Code docs: `CLAUDE_CODE_INSTALLATION.md`
For security: `SECURITY_GUIDE.md`

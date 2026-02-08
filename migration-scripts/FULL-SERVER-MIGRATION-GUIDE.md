# Complete Server Migration Guide
**From:** VPS 187.77.1.7 (ID: 1343427)
**To:** New Hostinger VPS

## Overview

This guide covers migrating **everything** from your current VPS to a new one:
- OpenClaw installation (/docker)
- Shared folders (/shared: openclaw, projects, scripts)
- Git configuration and repositories
- SSH keys and configuration
- Firewall rules (UFW)
- System packages
- Cron jobs
- All security configurations

## Current Server Inventory

### Main Components
```
/docker/openclaw-r8v9/        - OpenClaw installation (834M)
  ├── docker-compose.yml
  ├── .env
  └── data/
      ├── .openclaw/          - OpenClaw config & workspace
      ├── .claude/            - Claude Code state
      └── my-projects/        - User projects

/shared/                      - Shared data folders
  ├── openclaw/
  ├── projects/               - Git repositories
  └── scripts/                - Custom scripts

/root/.ssh/                   - SSH keys
  ├── id_ed25519              - Private key
  ├── id_ed25519.pub          - Public key
  └── authorized_keys

Firewall: UFW active
  - SSH (22/tcp): ALLOW
  - OpenClaw (59388/tcp): DENY
```

### Security Items
- **API Keys**: Anthropic, OpenAI, Gemini, Perplexity, Brave
- **Bot Tokens**: Discord, Gateway auth
- **SSH Keys**: Ed25519 keypair
- **Firewall Rules**: UFW configured

## Migration Options

### Option 1: Full Server Migration (Recommended for Complete Setup)

Migrates everything including OpenClaw, shared folders, and all configurations.

**Best for:**
- Complete server replication
- Preserving all Git repositories
- Maintaining exact same setup

**Commands:**
```bash
# Current server
/root/full-server-backup.sh production-migration
/root/full-server-transfer.sh <NEW_IP>

# New server
/root/full-server-restore.sh /root/server-backup-*.tar.gz.enc
```

### Option 2: OpenClaw Only Migration

Migrates just the OpenClaw installation.

**Best for:**
- Fresh server setup
- Only need OpenClaw
- Want to reconfigure other parts

**Commands:**
```bash
# Current server
/root/openclaw-backup.sh openclaw-only
/root/openclaw-transfer-to-new-server.sh <NEW_IP>

# New server
/root/openclaw-restore.sh /root/openclaw-backup-*.tar.gz.enc
```

## Step-by-Step: Full Server Migration

### Phase 1: Preparation (15 minutes)

#### On Current Server

1. **Verify current setup:**
   ```bash
   /root/test-migration-readiness.sh
   ```

2. **Document current state:**
   ```bash
   # Check sizes
   du -sh /docker /shared

   # List Git repos
   find /shared -name ".git" -type d

   # Check running services
   docker ps
   ```

3. **Optional: Stop services (if needed):**
   ```bash
   cd /docker/openclaw-r8v9
   docker compose down
   ```

#### On New Server

1. **Verify access:**
   ```bash
   ssh root@<NEW_IP>
   ```

2. **Check disk space:**
   ```bash
   df -h
   # Need at least: current usage + 50% buffer
   ```

### Phase 2: Backup (10-15 minutes)

On current server:

```bash
# Create complete backup
/root/full-server-backup.sh migration-$(date +%Y%m%d)

# Verify backup created
ls -lh /root/server-backups/
```

**What gets backed up:**
- ✓ Complete /docker directory
- ✓ Complete /shared directory
- ✓ SSH keys and config
- ✓ Git configuration
- ✓ Firewall rules (UFW)
- ✓ Installed packages list
- ✓ Cron jobs
- ✓ Environment variables
- ✓ Network configuration

### Phase 3: Transfer (15-30 minutes)

**Automated transfer:**
```bash
/root/full-server-transfer.sh <NEW_IP> [SSH_PORT]
```

**Manual transfer (if automated fails):**
```bash
# Get backup file name
BACKUP=$(ls -t /root/server-backups/*.tar.gz.enc | head -1)

# Transfer with rsync (resumable)
rsync -avz --progress -e "ssh -p 22" \
  $BACKUP root@<NEW_IP>:/root/

# Transfer scripts
scp /root/full-server-*.sh root@<NEW_IP>:/root/
scp /root/*.md root@<NEW_IP>:/root/
```

### Phase 4: New Server Setup (10 minutes)

SSH to new server:
```bash
ssh root@<NEW_IP>
```

Install prerequisites:
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
apt install docker-compose-plugin -y

# Install utilities
apt install -y ufw git jq rsync openssl net-tools curl wget tree

# Create groups
groupadd devs 2>/dev/null || true

# Make scripts executable
chmod +x /root/*.sh
```

### Phase 5: Restore (15-20 minutes)

```bash
# Run restore
/root/full-server-restore.sh /root/server-backup-*.tar.gz.enc

# Enter password when prompted (default: CHANGE_THIS_PASSWORD)
```

**The restore script will ask about:**
1. Continue with restore? → yes
2. Restore firewall rules? → yes (recommended)
3. Restore root crontab? → yes (if you had cron jobs)
4. Install packages from backup? → optional (can take long time)

### Phase 6: Configuration Review (10 minutes)

Before starting services, verify these files:

```bash
# 1. Check Docker Compose port configuration
nano /docker/openclaw-r8v9/docker-compose.yml

# 2. Check environment variables
nano /docker/openclaw-r8v9/.env
# Verify:
# - PORT matches docker-compose.yml
# - API keys are correct
# - Timezone is correct

# 3. Check OpenClaw configuration
nano /docker/openclaw-r8v9/data/.openclaw/openclaw.json
# Verify:
# - gateway.port (line 112)
# - gateway.bind (line 114)
# - workspace path (line 49)

# 4. Verify shared folders exist
ls -la /shared/

# 5. Check SSH keys were restored
ls -la /root/.ssh/
```

### Phase 7: Start Services (5 minutes)

```bash
# Start Docker containers
cd /docker/openclaw-r8v9
docker compose up -d

# Check container status
docker ps

# View logs
docker compose logs -f
# Press Ctrl+C to stop viewing logs
```

### Phase 8: Verification (10 minutes)

```bash
# Run verification script
/root/verify-server-migration.sh

# Manual checks:
# 1. Gateway accessible
curl http://localhost:18789/health

# 2. Workspace intact
ls -la /docker/openclaw-r8v9/data/.openclaw/workspace/

# 3. Shared folders intact
ls -la /shared/projects/

# 4. Git repos still work
cd /shared/projects/<some-repo>
git status

# 5. Firewall active
ufw status
```

### Phase 9: Final Configuration (10 minutes)

#### Update IP-Specific Settings

If you had any hardcoded IPs, update them:

```bash
# Search for old IP in configs
grep -r "187.77.1.7" /docker /shared /etc 2>/dev/null

# Update as needed
```

#### Configure External Access (if needed)

```bash
# Allow OpenClaw port through firewall
ufw allow 59388/tcp

# Verify
ufw status
```

#### Update DNS (if using domain)

If you have a domain pointing to the old server:
1. Update A record to new server IP
2. Wait for DNS propagation (up to 48 hours)
3. Test: `nslookup yourdomain.com`

### Phase 10: Testing (15-30 minutes)

**Critical Tests:**

1. **Docker Health:**
   ```bash
   docker ps  # All containers should be "Up"
   docker compose logs | grep -i error  # Check for errors
   ```

2. **OpenClaw Functionality:**
   - Test Discord bot (send message)
   - Test agent task
   - Verify workspace access

3. **Git Repositories:**
   ```bash
   cd /shared/projects/<repo>
   git status
   git log --oneline -5
   ```

4. **SSH Access:**
   ```bash
   # From another machine, test SSH
   ssh root@<NEW_IP>
   ```

5. **Network Services:**
   ```bash
   # Check listening ports
   netstat -tuln | grep LISTEN
   ```

## Security Hardening on New Server

### 1. Change Default Passwords

```bash
# Update backup encryption password in scripts
nano /root/full-server-backup.sh
# Change: pass:"CHANGE_THIS_PASSWORD"
```

### 2. Regenerate Gateway Token (Optional)

```bash
# Generate new token
NEW_TOKEN=$(openssl rand -hex 16)

# Update in .env
nano /docker/openclaw-r8v9/.env
# Update OPENCLAW_GATEWAY_TOKEN=

# Update in openclaw.json
nano /docker/openclaw-r8v9/data/.openclaw/openclaw.json
# Update gateway.auth.token (line 120)
# Update gateway.remote.token (line 127)

# Restart services
cd /docker/openclaw-r8v9 && docker compose restart
```

### 3. Configure Firewall

```bash
# Reset UFW to start fresh
ufw --force reset

# Default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (CRITICAL - don't lock yourself out!)
ufw allow 22/tcp

# Allow OpenClaw (adjust port if needed)
ufw allow 59388/tcp

# Enable firewall
ufw --force enable

# Verify
ufw status verbose
```

### 4. Secure File Permissions

```bash
# SSH keys
chmod 700 /root/.ssh
chmod 600 /root/.ssh/id_*
chmod 644 /root/.ssh/*.pub
chmod 600 /root/.ssh/authorized_keys

# Configuration files
chmod 600 /docker/openclaw-r8v9/.env
chmod 600 /docker/openclaw-r8v9/data/.openclaw/openclaw.json

# Data directories
chown -R 1000:1000 /docker/openclaw-r8v9/data
chmod -R g+w /shared
chgrp -R devs /shared
```

### 5. Update System

```bash
apt update
apt upgrade -y
apt autoremove -y
```

## Rollback Procedure

If something goes wrong:

### Immediate Rollback

The original server (187.77.1.7) is **unchanged**. You can:
1. Continue using it immediately
2. No data loss
3. No configuration changes

### Fix and Retry on New Server

```bash
# Stop services
cd /docker/openclaw-r8v9
docker compose down

# Remove installation
rm -rf /docker
rm -rf /shared

# Re-run restore with fixes
/root/full-server-restore.sh /root/server-backup-*.tar.gz.enc
```

## Post-Migration Checklist

### Immediate (Day 1)
- [ ] All containers running
- [ ] No errors in logs
- [ ] Discord/Slack integration working
- [ ] Workspace accessible
- [ ] Git repositories accessible
- [ ] Firewall configured
- [ ] SSH access working
- [ ] API keys validated

### Short-term (Week 1)
- [ ] DNS updated (if applicable)
- [ ] External services updated with new IP
- [ ] Monitoring set up
- [ ] Backups scheduled on new server
- [ ] Old server still available as fallback
- [ ] Performance verified
- [ ] All integrations tested

### Long-term (Month 1)
- [ ] Old server decommissioned
- [ ] Backups from old server securely deleted
- [ ] Documentation updated
- [ ] Team notified of new server details
- [ ] Automated backup tested on new server

## Troubleshooting

### Docker Containers Won't Start

```bash
# Check logs
docker compose logs

# Check configuration syntax
docker compose config

# Check port conflicts
netstat -tuln | grep <PORT>

# Verify ownership
ls -la /docker/openclaw-r8v9/data
# Should be: drwxr-xr-x ubuntu ubuntu
```

### Permission Errors

```bash
# Fix Docker data permissions
chown -R 1000:1000 /docker/openclaw-r8v9/data

# Fix shared folder permissions
chmod -R g+w /shared
chgrp -R devs /shared
```

### Git Repositories Not Working

```bash
# Re-add safe directories
cd /shared/projects/<repo>
git config --global --add safe.directory $(pwd)

# Check Git config
git config --global --list
```

### Firewall Blocking Access

```bash
# Check UFW status
ufw status verbose

# Temporarily disable to test
ufw disable

# If that fixes it, re-enable and add rule
ufw enable
ufw allow <PORT>/tcp
```

### SSH Connection Issues

```bash
# Check SSH service
systemctl status sshd

# Check SSH configuration
nano /etc/ssh/sshd_config
# Verify: PermitRootLogin yes (or your setting)

# Restart SSH
systemctl restart sshd
```

## Backup Schedule on New Server

Set up automated backups:

```bash
# Create daily backup cron job
crontab -e

# Add this line (daily at 2 AM):
0 2 * * * /root/full-server-backup.sh daily-$(date +\%Y\%m\%d) >> /var/log/backup.log 2>&1

# Weekly backup (Sundays at 3 AM):
0 3 * * 0 /root/full-server-backup.sh weekly-$(date +\%Y\%m\%d) >> /var/log/backup.log 2>&1
```

## Migration Timeline Summary

| Phase | Duration | Description |
|-------|----------|-------------|
| Preparation | 15 min | Document, verify, plan |
| Backup | 10-15 min | Create full backup |
| Transfer | 15-30 min | Upload to new server |
| New Server Setup | 10 min | Install Docker, tools |
| Restore | 15-20 min | Extract and configure |
| Configuration | 10 min | Review and update configs |
| Start Services | 5 min | Launch containers |
| Verification | 10 min | Run tests |
| Final Config | 10 min | Firewall, DNS, etc. |
| Testing | 15-30 min | Comprehensive testing |
| **TOTAL** | **2-3 hours** | Complete migration |

## Quick Command Reference

### Backup
```bash
/root/full-server-backup.sh <name>
```

### Transfer
```bash
rsync -avz --progress <backup>.tar.gz.enc root@<IP>:/root/
```

### Restore
```bash
/root/full-server-restore.sh /root/<backup>.tar.gz.enc
```

### Start/Stop Services
```bash
cd /docker/openclaw-r8v9
docker compose up -d      # Start
docker compose down       # Stop
docker compose restart    # Restart
docker compose logs -f    # Logs
```

### Verification
```bash
/root/verify-server-migration.sh
```

## Support Files

All migration scripts and documentation:

```
/root/
├── full-server-backup.sh           - Complete backup
├── full-server-restore.sh          - Complete restore
├── full-server-transfer.sh         - Automated transfer
├── verify-server-migration.sh      - Verify installation
├── openclaw-backup.sh              - OpenClaw only backup
├── openclaw-restore.sh             - OpenClaw only restore
├── openclaw-transfer-to-new-server.sh - OpenClaw transfer
├── FULL-SERVER-MIGRATION-GUIDE.md  - This file
├── QUICK-START-MIGRATION.md        - Quick reference
└── MIGRATION-README.md             - Overview
```

## Final Notes

1. **Keep Original Server Running**
   - Don't decommission for at least 48 hours
   - Use as fallback if issues arise
   - Verify all functionality before shutdown

2. **Backup Encryption**
   - Default password: `CHANGE_THIS_PASSWORD`
   - Change before production use
   - Store password securely

3. **Testing is Critical**
   - Test all integrations
   - Verify all services
   - Check all Git repositories
   - Validate all API keys

4. **Documentation**
   - Document new server IP
   - Update team documentation
   - Record any changes made
   - Keep migration notes

---

**Ready to migrate?** Start with `/root/full-server-backup.sh`

**Questions?** Review troubleshooting section or check individual script help

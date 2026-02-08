# Server Migration - START HERE

## Quick Decision: Which Migration Do You Need?

### ✅ I want to migrate EVERYTHING
- OpenClaw + Shared folders + Git repos + All configs
- **→ Use: Full Server Migration**
- **→ Read:** `/root/FULL-SERVER-MIGRATION-GUIDE.md`
- **→ Run:** `/root/full-server-backup.sh`

### ✅ I only want to migrate OpenClaw
- Just the OpenClaw installation
- **→ Use: OpenClaw Only Migration**
- **→ Read:** `/root/QUICK-START-MIGRATION.md`
- **→ Run:** `/root/openclaw-backup.sh`

---

## Full Server Migration (RECOMMENDED)

### What Gets Migrated
- ✓ OpenClaw (/docker/openclaw-r8v9) - 834M
- ✓ Shared folders (/shared) - openclaw, projects, scripts
- ✓ Git configuration and all repositories
- ✓ SSH keys and configuration
- ✓ Firewall rules (UFW)
- ✓ API keys and tokens
- ✓ Cron jobs
- ✓ All security configurations

### One-Command Quick Start
```bash
# 1. Create backup
/root/full-server-backup.sh production

# 2. Transfer to new server (all-in-one)
# Coming soon: /root/full-server-transfer.sh <NEW_IP>

# Or manually:
scp /root/server-backups/production.tar.gz.enc root@<NEW_IP>:/root/

# 3. On new server:
/root/full-server-restore.sh /root/production.tar.gz.enc
cd /docker/openclaw-r8v9 && docker compose up -d
```

### Time Required
- Backup: 10-15 minutes
- Transfer: 15-30 minutes (depends on size/speed)
- Restore: 15-20 minutes
- **Total: ~1-2 hours** (including testing)

---

## OpenClaw Only Migration

### What Gets Migrated
- ✓ OpenClaw installation only
- ✓ Configuration files
- ✓ Workspace data
- ✓ API keys

### One-Command Quick Start
```bash
# 1. Transfer everything (backup + transfer)
/root/openclaw-transfer-to-new-server.sh <NEW_IP>

# 2. On new server:
/root/setup-new-server.sh
/root/openclaw-restore.sh /root/openclaw-backup-*.tar.gz.enc
cd /docker/openclaw-r8v9 && docker compose up -d
```

### Time Required
- **Total: ~30-60 minutes**

---

## Current Server Inventory

**Server:** 187.77.1.7 (VPS ID: 1343427)

```
Total Size: ~834M

/docker/openclaw-r8v9/
├── OpenClaw installation
├── Configuration files
└── Workspace (50M)

/shared/
├── openclaw/
├── projects/          (Git repositories)
└── scripts/           (Custom scripts)

Security:
├── SSH keys (Ed25519)
├── API keys (Anthropic, OpenAI, Gemini, etc.)
├── Bot tokens (Discord, Gateway)
└── Firewall (UFW active)
```

---

## Available Scripts

### Backup Scripts
- `full-server-backup.sh` - Complete server backup
- `openclaw-backup.sh` - OpenClaw only backup

### Restore Scripts
- `full-server-restore.sh` - Complete server restore
- `openclaw-restore.sh` - OpenClaw only restore

### Transfer Scripts
- `openclaw-transfer-to-new-server.sh` - Automated OpenClaw transfer
- Manual transfer: use `scp` or `rsync`

### Verification Scripts
- `verify-server-migration.sh` - Verify complete migration
- `openclaw-verify.sh` - Verify OpenClaw only
- `test-migration-readiness.sh` - Check if ready to migrate

### Documentation
- `FULL-SERVER-MIGRATION-GUIDE.md` - Complete guide (recommended!)
- `QUICK-START-MIGRATION.md` - Quick reference
- `MIGRATION-README.md` - Package overview
- `openclaw-migration-guide.md` - OpenClaw specific guide

---

## Step-by-Step for Complete Migration

### Current Server (187.77.1.7)

**Step 1: Test readiness**
```bash
/root/test-migration-readiness.sh
```

**Step 2: Create backup**
```bash
/root/full-server-backup.sh my-migration
```

**Step 3: Transfer to new server**
```bash
# Get backup file
ls -lh /root/server-backups/

# Transfer (encrypted - recommended)
scp /root/server-backups/my-migration.tar.gz.enc root@<NEW_IP>:/root/

# Also transfer scripts
scp /root/full-server-*.sh root@<NEW_IP>:/root/
scp /root/*.md root@<NEW_IP>:/root/
```

### New Server

**Step 1: Install prerequisites**
```bash
# Docker
curl -fsSL https://get.docker.com | sh
apt install docker-compose-plugin -y

# Utilities
apt install -y ufw git jq rsync openssl net-tools

# Groups
groupadd devs

# Make scripts executable
chmod +x /root/*.sh
```

**Step 2: Restore**
```bash
/root/full-server-restore.sh /root/my-migration.tar.gz.enc
# Password: CHANGE_THIS_PASSWORD
```

**Step 3: Start services**
```bash
cd /docker/openclaw-r8v9
docker compose up -d
```

**Step 4: Verify**
```bash
/root/verify-server-migration.sh
docker ps
docker compose logs
```

---

## Critical Security Notes

### Default Password
**Backup encryption password:** `CHANGE_THIS_PASSWORD`

**⚠️ IMPORTANT:** Change this before production use!

Edit the password in:
- `/root/full-server-backup.sh` (line with openssl enc)
- `/root/openclaw-backup.sh` (line with openssl enc)

### What Contains Sensitive Data

Backups include:
- SSH private keys
- API keys (Anthropic, OpenAI, Gemini, Perplexity, Brave)
- Discord/Slack bot tokens
- Gateway authentication tokens
- Firewall configurations

**Must do:**
1. ✓ Transfer only encrypted archives
2. ✓ Use secure methods (SCP/SSH, not FTP)
3. ✓ Delete unencrypted archives after transfer
4. ✓ chmod 600 all backup files
5. ✓ Store encryption password securely

---

## Firewall Configuration

**Current firewall rules:**
```
SSH (22/tcp): ALLOW
OpenClaw (59388/tcp): DENY
```

On new server, configure firewall BEFORE enabling:
```bash
ufw allow 22/tcp        # SSH - CRITICAL!
ufw allow 59388/tcp     # OpenClaw (adjust if needed)
ufw enable
```

---

## Troubleshooting

### Migration won't start
```bash
# Check readiness
/root/test-migration-readiness.sh

# Verify disk space
df -h

# Check Docker
systemctl status docker
```

### Transfer failed
```bash
# Use rsync for resumable transfer
rsync -avz --progress --partial \
  /root/server-backups/*.tar.gz.enc \
  root@<NEW_IP>:/root/
```

### Restore failed
```bash
# Check backup integrity
cd /tmp
tar tzf /root/backup.tar.gz.enc  # Should list files

# Check permissions
ls -la /root/*.tar.gz.enc
chmod 600 /root/*.tar.gz.enc
```

### Services won't start
```bash
# Check logs
docker compose logs

# Check ports
netstat -tuln | grep 59388

# Fix permissions
chown -R 1000:1000 /docker/openclaw-r8v9/data
```

---

## Need Help?

1. **Full migration guide:** `/root/FULL-SERVER-MIGRATION-GUIDE.md`
2. **Quick reference:** `/root/QUICK-START-MIGRATION.md`
3. **Run verification:** `/root/test-migration-readiness.sh`
4. **Check logs:** Look for error messages in script output

---

## Next Steps

### For Full Server Migration:
```bash
# 1. Read the complete guide
less /root/FULL-SERVER-MIGRATION-GUIDE.md

# 2. Test readiness
/root/test-migration-readiness.sh

# 3. Create backup
/root/full-server-backup.sh production
```

### For OpenClaw Only:
```bash
# 1. Read quick start
less /root/QUICK-START-MIGRATION.md

# 2. Run transfer
/root/openclaw-transfer-to-new-server.sh <NEW_IP>
```

---

## Migration Checklist

Before starting:
- [ ] New VPS IP address ready
- [ ] SSH access to new VPS confirmed
- [ ] Disk space verified on new VPS (need ~1GB+)
- [ ] 1-2 hours available for migration
- [ ] Backup of current server (safety)

During migration:
- [ ] Backup created successfully
- [ ] Backup transferred to new server
- [ ] Restore completed without errors
- [ ] Services started successfully
- [ ] Verification passed

After migration:
- [ ] All services working
- [ ] Git repositories accessible
- [ ] Integrations (Discord, etc.) working
- [ ] Firewall configured
- [ ] Keep original server for 24-48h as fallback

---

**Ready? Start here:**

```bash
# For everything:
less /root/FULL-SERVER-MIGRATION-GUIDE.md
/root/full-server-backup.sh

# For just OpenClaw:
less /root/QUICK-START-MIGRATION.md
/root/openclaw-transfer-to-new-server.sh <NEW_IP>
```

**Questions?** All scripts have built-in help and detailed error messages.

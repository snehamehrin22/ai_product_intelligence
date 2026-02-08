# OpenClaw Migration Package - README

**Created:** $(date)
**Current Server:** 187.77.1.7 (VPS ID: 1343427)
**OpenClaw Location:** /docker/openclaw-r8v9/

## What This Package Contains

This complete migration package includes everything you need to safely migrate your OpenClaw installation to a new Hostinger VPS.

### Scripts

1. **openclaw-backup.sh** (6.2K)
   - Creates comprehensive backup of entire OpenClaw installation
   - Includes encrypted and unencrypted archive options
   - Generates checksums for verification
   - Creates detailed backup manifest

2. **openclaw-restore.sh** (5.5K)
   - Restores OpenClaw from backup archive
   - Handles both encrypted and unencrypted backups
   - Verifies backup integrity
   - Sets correct permissions

3. **openclaw-verify.sh** (7.8K)
   - Comprehensive verification of installation
   - Checks 10+ critical components
   - Validates configuration files
   - Tests Docker containers and networking

4. **openclaw-transfer-to-new-server.sh** (6.6K)
   - Automated one-command migration
   - Transfers backup and scripts to new server
   - Creates setup script for new server
   - Tests SSH connectivity

### Documentation

5. **openclaw-migration-guide.md** (11K)
   - Complete step-by-step migration guide
   - Security considerations
   - Troubleshooting section
   - Rollback procedures

6. **QUICK-START-MIGRATION.md** (6.5K)
   - Quick reference for migration
   - Two migration paths (automated/manual)
   - Configuration checklist
   - Common commands

7. **MIGRATION-README.md** (this file)
   - Overview of the migration package
   - Quick decision guide
   - Common scenarios

## What Gets Backed Up

### Critical Configuration
- Docker Compose configuration (`docker-compose.yml`)
- Environment variables (`.env`) including:
  - PORT=59388
  - Timezone settings
  - All API keys and tokens

### OpenClaw Configuration
- Main config: `.openclaw/openclaw.json`
  - Agent settings (model: google/gemini-3-flash)
  - Context tokens: 200,000
  - Compaction mode: safeguard
  - Workspace path
  - Gateway configuration (port: 18789)
  - Plugin settings (Discord, WhatsApp, Telegram, Slack, etc.)

### Security & Authentication
- Device authentication (`.openclaw/identity/`)
- Paired devices (`.openclaw/devices/`)
- Execution approvals (`.openclaw/exec-approvals.json`)
- API Keys:
  - Anthropic (Claude)
  - OpenAI
  - Gemini
  - Perplexity
  - Brave Search
- Bot Tokens:
  - Discord
  - Gateway authentication

### Data
- Agent workspace (`.openclaw/workspace/`)
- Claude state (`.claude/` and `.claude.json`)
- Cron jobs (`.openclaw/cron/`)
- Subagent runs (`.openclaw/subagents/`)
- User projects (`my-projects/`)

## Quick Decision Guide

### "I want the simplest, fastest migration"
**→ Use the automated transfer script**

```bash
/root/openclaw-transfer-to-new-server.sh <NEW_SERVER_IP>
```

Then on new server:
```bash
/root/setup-new-server.sh
/root/openclaw-restore.sh /root/openclaw-backup-*.tar.gz.enc
cd /docker/openclaw-r8v9 && docker compose up -d
```

### "I want to test the backup first"
**→ Create a backup and verify it**

```bash
/root/openclaw-backup.sh test-backup
ls -lh /root/openclaw-backups/
cat /root/openclaw-backups/test-backup/BACKUP-SUMMARY.txt
```

### "I have a slow or unreliable connection"
**→ Use the manual method with rsync**

```bash
# Create backup
/root/openclaw-backup.sh production-backup

# Transfer with resumable rsync
rsync -avz --progress --partial \
  /root/openclaw-backups/production-backup.tar.gz.enc \
  root@<NEW_IP>:/root/
```

### "I want maximum security"
**→ Use encrypted backup with custom password**

1. Edit `/root/openclaw-backup.sh`
2. Change line with `pass:"CHANGE_THIS_PASSWORD"`
3. Run: `/root/openclaw-backup.sh secure-backup`
4. Transfer only the .enc file (delete .tar.gz)

### "I need to migrate but keep this server running"
**→ Perfect! That's the recommended approach**

The migration process doesn't affect your current server. You can:
1. Create backup while OpenClaw runs
2. Transfer to new server
3. Test new server thoroughly
4. Keep both running until confident
5. Switch DNS/traffic when ready

## Common Migration Scenarios

### Scenario 1: Direct Server-to-Server (Both on Hostinger)

```bash
# Get new server IP from Hostinger panel
NEW_IP="x.x.x.x"

# Run automated transfer
/root/openclaw-transfer-to-new-server.sh $NEW_IP

# SSH to new server and complete setup
ssh root@$NEW_IP
/root/setup-new-server.sh
/root/openclaw-restore.sh /root/openclaw-backup-*.tar.gz.enc
cd /docker/openclaw-r8v9 && docker compose up -d
```

### Scenario 2: Transfer via Local Machine

```bash
# On current server - create backup
/root/openclaw-backup.sh my-backup

# Download to local machine
scp root@187.77.1.7:/root/openclaw-backups/my-backup.tar.gz.enc ~/

# Upload to new server
scp ~/my-backup.tar.gz.enc root@<NEW_IP>:/root/

# SSH to new and restore
ssh root@<NEW_IP>
# ... follow setup steps
```

### Scenario 3: Upgrade OS During Migration

If new server has different OS version:

```bash
# Create backup normally
/root/openclaw-backup.sh os-upgrade-backup

# Transfer to new server
# On new server:
/root/setup-new-server.sh  # Installs Docker for new OS
/root/openclaw-restore.sh /root/os-upgrade-backup.tar.gz.enc

# Verify compatibility
/root/openclaw-verify.sh
docker compose logs  # Check for any OS-specific issues
```

## Pre-Migration Checklist

Before starting migration:

- [ ] Current OpenClaw is working properly
- [ ] You have new VPS details (IP address, SSH access)
- [ ] New VPS has sufficient disk space (current usage + 50%)
- [ ] You have 30-60 minutes available
- [ ] You've documented any custom configurations
- [ ] You've notified users of potential brief downtime (optional)

## Migration Timeline

| Phase | Duration | Description |
|-------|----------|-------------|
| Backup | 5-10 min | Create backup of current installation |
| Transfer | 10-30 min | Upload to new server (depends on size/speed) |
| Setup | 5-10 min | Install Docker and dependencies |
| Restore | 10-15 min | Extract and configure on new server |
| Testing | 15-30 min | Verify everything works |
| **Total** | **45-95 min** | Complete migration |

## Critical Security Notes

### API Keys Included in Backup

The backup contains sensitive API keys:
- **Anthropic API Key**: sk-ant-api03-IsO6ybV...
- **OpenAI API Key**: sk-proj-SBbHns_FC...
- **Discord Token**: MTQ2OTU3ODk2NDI2...
- **Gateway Token**: oIdm3sJyG0nhm4Zi...
- **Gemini API Key**: AIzaSyAJGj_q2_eE...
- **Perplexity API Key**: pplx-pydD5yYUBy...
- **Brave Search Key**: BSAJczT_TwZgZ_U...

**Action Items:**
1. Use encrypted backup (`.tar.gz.enc`) for transfer
2. Delete unencrypted backups after successful migration
3. Consider regenerating gateway tokens post-migration
4. Verify API key validity on new server
5. Never commit backups to version control
6. Use secure transfer methods (SCP/SSH, not FTP)

### File Permissions

After restore, verify these permissions:

```bash
chmod 600 /docker/openclaw-r8v9/.env
chmod 600 /docker/openclaw-r8v9/data/.openclaw/openclaw.json
chmod 600 /docker/openclaw-r8v9/data/.openclaw/identity/*
chown -R 1000:1000 /docker/openclaw-r8v9/data
```

## Testing on New Server

Before switching production traffic:

1. **Container Health**
   ```bash
   docker ps  # Should show running containers
   docker compose logs  # No errors
   ```

2. **Gateway Access**
   ```bash
   curl http://localhost:18789/health
   ```

3. **Configuration**
   ```bash
   /root/openclaw-verify.sh  # Should pass all checks
   ```

4. **Discord/Slack Integration**
   - Send a test message
   - Verify bot responds
   - Check it can access workspace

5. **Agent Functionality**
   - Test a simple agent task
   - Verify workspace access
   - Check API calls work

## Rollback Plan

If something goes wrong:

1. **Current server (187.77.1.7) is unchanged**
   - Original installation still works
   - Can continue using immediately

2. **New server can be reset**
   - Stop containers: `docker compose down`
   - Delete installation: `rm -rf /docker/openclaw-r8v9`
   - Re-run restore with corrections

3. **Backup is safe**
   - Multiple backup copies available
   - Can restore to original server if needed
   - Can create new backup anytime

## Support & Troubleshooting

### Common Issues

**Issue**: "Permission denied" during backup
- **Solution**: Run scripts with `sudo` or as root

**Issue**: "Cannot connect to new server"
- **Solution**: Check firewall, SSH port, IP address

**Issue**: "Docker not found" on new server
- **Solution**: Run `/root/setup-new-server.sh`

**Issue**: "Checksum verification failed"
- **Solution**: Transfer may have corrupted, re-transfer backup

**Issue**: "Container won't start"
- **Solution**: Check logs with `docker compose logs`, verify ports not in use

### Getting Help

1. Check `/root/openclaw-migration-guide.md` - detailed troubleshooting
2. Review script output - errors are color-coded (red)
3. Check Docker logs - `docker compose logs -f`
4. Verify script in `/root/openclaw-verify.sh`

## After Migration

### Immediate (Within 24 hours)
- [ ] Run verification script
- [ ] Test all integrations
- [ ] Monitor logs for errors
- [ ] Update DNS if using domain
- [ ] Test from external clients

### Short-term (Within 1 week)
- [ ] Set up automated backups on new server
- [ ] Update documentation with new IP
- [ ] Decommission old server (after confirming stable)
- [ ] Securely delete backups from old server
- [ ] Update any hardcoded IPs in external services

### Long-term
- [ ] Schedule monthly backup tests
- [ ] Document any configuration changes
- [ ] Review and update API keys as needed
- [ ] Monitor disk usage and performance

## Quick Command Reference

### Create Backup
```bash
/root/openclaw-backup.sh [backup-name]
```

### Transfer to New Server
```bash
/root/openclaw-transfer-to-new-server.sh <NEW_IP> [SSH_PORT]
```

### Restore (On New Server)
```bash
/root/openclaw-restore.sh <backup-file.tar.gz.enc>
```

### Verify Installation
```bash
/root/openclaw-verify.sh
```

### Start/Stop OpenClaw
```bash
cd /docker/openclaw-r8v9
docker compose up -d      # Start
docker compose down       # Stop
docker compose restart    # Restart
docker compose logs -f    # View logs
```

## File Locations Reference

**Current Server (187.77.1.7):**
- OpenClaw: `/docker/openclaw-r8v9/`
- Backups: `/root/openclaw-backups/`
- Scripts: `/root/openclaw-*.sh`
- Docs: `/root/*.md`

**New Server (After Migration):**
- OpenClaw: `/docker/openclaw-r8v9/`
- Scripts: `/root/openclaw-*.sh`
- Docs: `/root/*.md`

## Package Version Info

- **Scripts Created**: February 8, 2026
- **OpenClaw Version**: 2026.2.3
- **Docker Image**: ghcr.io/hostinger/hvps-openclaw:latest
- **Tested On**: Ubuntu Linux

---

## Ready to Start?

**For automated migration:**
```bash
/root/openclaw-transfer-to-new-server.sh <NEW_SERVER_IP>
```

**For step-by-step guidance:**
```bash
less /root/QUICK-START-MIGRATION.md
```

**For detailed reference:**
```bash
less /root/openclaw-migration-guide.md
```

---

**Questions or issues?** All scripts have built-in help and error messages. The verification script will identify any problems after migration.

**Remember:** Your current server remains untouched during migration. You can test thoroughly before switching over.

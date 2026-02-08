# OpenClaw Migration - Quick Start Guide

**Current VPS:** 187.77.1.7 (VPS ID: 1343427)
**Target:** New Hostinger VPS

## Prerequisites

### On Current VPS (187.77.1.7)
- All scripts are already created in `/root/`
- OpenClaw is running in `/docker/openclaw-r8v9/`

### On New VPS
- Ubuntu 22.04 (or compatible OS)
- Root SSH access
- Sufficient disk space (check current: `du -sh /docker/openclaw-r8v9`)

## Migration Options

### Option 1: Automated Transfer (Recommended)

Single command to backup, transfer, and set up everything:

```bash
# On current VPS (187.77.1.7)
chmod +x /root/openclaw-transfer-to-new-server.sh
/root/openclaw-transfer-to-new-server.sh <NEW_SERVER_IP> [SSH_PORT]

# Examples:
/root/openclaw-transfer-to-new-server.sh 192.168.1.100
/root/openclaw-transfer-to-new-server.sh 192.168.1.100 2222
```

This will:
1. Create a backup if one doesn't exist
2. Test SSH connection to new server
3. Transfer backup archive (encrypted)
4. Transfer all migration scripts
5. Create setup script for new server

Then on the **new server**:

```bash
# 1. Run setup (installs Docker, utilities)
chmod +x /root/setup-new-server.sh
/root/setup-new-server.sh

# 2. Restore OpenClaw
/root/openclaw-restore.sh /root/openclaw-backup-*.tar.gz.enc
# Password: CHANGE_THIS_PASSWORD

# 3. Start OpenClaw
cd /docker/openclaw-r8v9
docker compose up -d

# 4. Verify
/root/openclaw-verify.sh
```

### Option 2: Manual Step-by-Step

#### Step 1: Create Backup (Current VPS)

```bash
chmod +x /root/openclaw-backup.sh
/root/openclaw-backup.sh migration-backup
```

#### Step 2: Transfer to New VPS

```bash
# Transfer encrypted backup
scp /root/openclaw-backups/migration-backup.tar.gz.enc root@<NEW_IP>:/root/

# Transfer scripts
scp /root/openclaw-{restore,verify}.sh root@<NEW_IP>:/root/
scp /root/openclaw-migration-guide.md root@<NEW_IP>:/root/
```

#### Step 3: Set Up New VPS

```bash
# SSH to new server
ssh root@<NEW_IP>

# Install Docker
curl -fsSL https://get.docker.com | sh
apt install docker-compose-plugin -y

# Install utilities
apt install -y jq openssl rsync net-tools

# Make scripts executable
chmod +x /root/openclaw-restore.sh
chmod +x /root/openclaw-verify.sh
```

#### Step 4: Restore on New VPS

```bash
# Restore from backup
/root/openclaw-restore.sh /root/migration-backup.tar.gz.enc

# Start OpenClaw
cd /docker/openclaw-r8v9
docker compose up -d

# Verify installation
/root/openclaw-verify.sh
```

## Configuration Files to Review

Before starting OpenClaw on the new server, check these files:

```bash
# 1. Environment variables (API keys, ports)
nano /docker/openclaw-r8v9/.env

# Key settings:
# - PORT=59388 (change if needed)
# - ANTHROPIC_API_KEY (verify)
# - OPENCLAW_GATEWAY_TOKEN (verify)

# 2. Docker Compose
nano /docker/openclaw-r8v9/docker-compose.yml

# 3. OpenClaw main config
nano /docker/openclaw-r8v9/data/.openclaw/openclaw.json

# Key settings:
# - gateway.port (line 112)
# - gateway.bind (line 114) - "loopback" for security
# - workspace path (line 49)
```

## Verification Checklist

After migration, verify:

- [ ] Containers running: `docker ps`
- [ ] Gateway accessible: `curl http://localhost:18789/health`
- [ ] Logs look good: `docker compose logs -f`
- [ ] Workspace intact: `ls -la /docker/openclaw-r8v9/data/.openclaw/workspace/`
- [ ] Configuration preserved: Check API keys work
- [ ] Discord/Slack bots connected (if applicable)
- [ ] Run verification: `/root/openclaw-verify.sh`

## Firewall Configuration (Important!)

```bash
# Allow SSH
ufw allow 22/tcp

# Allow OpenClaw port (check .env for your port)
ufw allow 59388/tcp

# Enable firewall
ufw enable
```

## Security Reminders

1. **Change backup password** in scripts before production use
2. **Verify API keys** are correct and not exposed
3. **Delete unencrypted backups** after successful migration:
   ```bash
   rm /root/openclaw-backups/*.tar.gz  # Keep only .enc files
   ```
4. **Set proper permissions**:
   ```bash
   chmod 600 /docker/openclaw-r8v9/.env
   ```

## Troubleshooting Quick Tips

### Container won't start
```bash
docker compose logs
docker compose config  # Check for syntax errors
```

### Permission issues
```bash
chown -R 1000:1000 /docker/openclaw-r8v9/data
```

### Port already in use
```bash
netstat -tuln | grep 59388
# Change PORT in .env if needed
```

### Gateway not accessible
```bash
# Check if running
docker ps | grep openclaw

# Check port mapping
docker port openclaw-r8v9-openclaw-1
```

## Rollback Plan

If migration fails:
1. Original server (187.77.1.7) still has working installation
2. Can restore from backup on original server if needed
3. Keep original server running for 24-48 hours as safety net

## DNS/Domain Updates (If Applicable)

If you use a custom domain:
1. Test thoroughly on new server using IP address
2. Update DNS A record to point to new server IP
3. Wait for DNS propagation (up to 48 hours)
4. Verify domain points to new server: `nslookup your-domain.com`

## Support Files Location

All scripts and guides are in `/root/`:
- `openclaw-backup.sh` - Create backups
- `openclaw-restore.sh` - Restore from backup
- `openclaw-verify.sh` - Verify installation
- `openclaw-transfer-to-new-server.sh` - Automated transfer
- `openclaw-migration-guide.md` - Detailed guide
- `QUICK-START-MIGRATION.md` - This file

## Backup Password

**Default password:** `CHANGE_THIS_PASSWORD`

**IMPORTANT:** Change this in `/root/openclaw-backup.sh` line with:
```bash
openssl enc -aes-256-cbc -salt -pbkdf2 -out "${ARCHIVE_FILE}" -pass pass:"YOUR_SECURE_PASSWORD"
```

## Timeline Estimate

- Backup creation: 5-10 minutes
- File transfer: 10-30 minutes (depends on size and network)
- New server setup: 5-10 minutes
- Restore and verification: 10-15 minutes

**Total: ~30-60 minutes** (plus testing time)

## Post-Migration

1. Test all features thoroughly
2. Monitor logs for any errors
3. Keep original server running for 24-48 hours
4. Once confirmed stable, document the new server details
5. Update any external services that point to the old IP
6. Schedule regular backups on new server

## Questions or Issues?

Refer to `/root/openclaw-migration-guide.md` for detailed troubleshooting and additional information.

---

**Quick Command Reference:**

```bash
# Current VPS - Create and transfer
/root/openclaw-transfer-to-new-server.sh <NEW_IP>

# New VPS - Setup
/root/setup-new-server.sh

# New VPS - Restore
/root/openclaw-restore.sh /root/openclaw-backup-*.tar.gz.enc

# New VPS - Start
cd /docker/openclaw-r8v9 && docker compose up -d

# New VPS - Verify
/root/openclaw-verify.sh
```

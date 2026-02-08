# OpenClaw Migration Guide

Complete guide for migrating OpenClaw from one VPS to another.

## Table of Contents

1. [Pre-Migration Checklist](#pre-migration-checklist)
2. [Backup Process](#backup-process)
3. [Transfer to New Server](#transfer-to-new-server)
4. [Restore Process](#restore-process)
5. [Post-Migration Verification](#post-migration-verification)
6. [Security Considerations](#security-considerations)
7. [Troubleshooting](#troubleshooting)

## Pre-Migration Checklist

### On the Source Server

- [ ] Document current OpenClaw version
- [ ] Document all enabled plugins
- [ ] Note any custom configurations
- [ ] Verify all services are working
- [ ] Stop active agent sessions (optional but recommended)
- [ ] Create a list of all integrated services (Discord, Slack, etc.)

### On the Target Server

- [ ] Install Docker and Docker Compose
- [ ] Ensure sufficient disk space (check current usage + 50%)
- [ ] Configure firewall rules for required ports
- [ ] Set up SSH access
- [ ] Install required tools: `jq`, `openssl`, `rsync`

## Backup Process

### 1. Run the Backup Script

```bash
# Make scripts executable
chmod +x /root/openclaw-backup.sh
chmod +x /root/openclaw-restore.sh
chmod +x /root/openclaw-verify.sh

# Run backup
sudo /root/openclaw-backup.sh my-migration-backup
```

### 2. Verify Backup

The backup will create:
- **Directory backup**: `/root/openclaw-backups/my-migration-backup/`
- **Encrypted archive**: `/root/openclaw-backups/my-migration-backup.tar.gz.enc`
- **Unencrypted archive**: `/root/openclaw-backups/my-migration-backup.tar.gz`

Check the backup summary:
```bash
cat /root/openclaw-backups/my-migration-backup/BACKUP-SUMMARY.txt
```

### 3. What Gets Backed Up

**Configuration Files:**
- `docker-compose.yml` - Container orchestration
- `.env` - Environment variables and secrets
- `.openclaw/openclaw.json` - Main OpenClaw configuration
- `.claude.json` - Claude Code settings

**Data & State:**
- `.openclaw/identity/` - Device authentication
- `.openclaw/devices/` - Paired devices
- `.openclaw/workspace/` - Agent workspace files
- `.openclaw/exec-approvals.json` - Command execution approvals
- `.claude/todos/` - Task lists and agent state
- `my-projects/` - User projects

**Security Items:**
- API Keys (Anthropic, OpenAI, Gemini, Perplexity, Brave)
- Discord/Slack/Telegram bot tokens
- Gateway authentication tokens
- Device authentication keys

## Transfer to New Server

### Option 1: Using SCP (Encrypted Archive - Recommended)

```bash
# From source server
scp /root/openclaw-backups/my-migration-backup.tar.gz.enc root@new-server-ip:/root/

# Or with custom SSH port
scp -P 2222 /root/openclaw-backups/my-migration-backup.tar.gz.enc root@new-server-ip:/root/
```

### Option 2: Using Rsync (More Reliable)

```bash
# From source server
rsync -avz --progress /root/openclaw-backups/my-migration-backup.tar.gz.enc root@new-server-ip:/root/

# With custom SSH port
rsync -avz --progress -e "ssh -p 2222" /root/openclaw-backups/my-migration-backup.tar.gz.enc root@new-server-ip:/root/
```

### Option 3: Using a Jump Server

If you can't directly connect between servers:

```bash
# Download to local machine
scp root@source-server:/root/openclaw-backups/my-migration-backup.tar.gz.enc ./

# Upload to new server
scp my-migration-backup.tar.gz.enc root@new-server:/root/
```

## Restore Process

### 1. Transfer Scripts to New Server

```bash
# Copy the restore and verify scripts to the new server
scp /root/openclaw-restore.sh root@new-server:/root/
scp /root/openclaw-verify.sh root@new-server:/root/
```

### 2. Install Prerequisites on New Server

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Install utilities
apt install -y jq openssl rsync net-tools

# Verify installations
docker --version
docker compose version
jq --version
```

### 3. Run Restore Script

```bash
# Make scripts executable
chmod +x /root/openclaw-restore.sh
chmod +x /root/openclaw-verify.sh

# Run restore
sudo /root/openclaw-restore.sh /root/my-migration-backup.tar.gz.enc

# Enter the backup password when prompted (default: CHANGE_THIS_PASSWORD)
```

### 4. Review Configuration

Before starting OpenClaw, review these files:

```bash
# Check environment variables
nano /docker/openclaw-r8v9/.env

# Check Docker Compose configuration
nano /docker/openclaw-r8v9/docker-compose.yml

# Check OpenClaw configuration
nano /docker/openclaw-r8v9/data/.openclaw/openclaw.json
```

**Important settings to verify:**
- Port numbers (ensure they don't conflict)
- Timezone settings
- Workspace path
- Gateway bind address (use "loopback" for localhost-only access)

### 5. Start OpenClaw

```bash
cd /docker/openclaw-r8v9
docker compose up -d

# Check logs
docker compose logs -f
```

## Post-Migration Verification

### 1. Run Verification Script

```bash
/root/openclaw-verify.sh
```

This will check:
- Directory structure
- Configuration files
- API keys and tokens
- Docker containers
- Network ports
- File permissions
- Security settings

### 2. Manual Verification Checklist

- [ ] OpenClaw containers are running
- [ ] Gateway is accessible (check configured port)
- [ ] API keys are working (test a simple agent command)
- [ ] Discord/Slack integration works (if configured)
- [ ] Workspace files are accessible
- [ ] Device authentication works
- [ ] Previous agent sessions are preserved (if needed)

### 3. Test Basic Functionality

```bash
# Check container status
docker ps

# Check gateway logs
docker logs openclaw-r8v9-openclaw-1

# Test API connectivity
curl http://localhost:18789/health 2>/dev/null || echo "Gateway not responding"
```

## Security Considerations

### Critical Security Steps

1. **Change Default Passwords**
   ```bash
   # Update the backup encryption password in scripts
   nano /root/openclaw-backup.sh
   # Change: pass:"CHANGE_THIS_PASSWORD"
   ```

2. **Regenerate Gateway Token (Optional)**
   ```bash
   # Generate new token
   NEW_TOKEN=$(openssl rand -hex 16)

   # Update in .env
   nano /docker/openclaw-r8v9/.env

   # Update in openclaw.json
   nano /docker/openclaw-r8v9/data/.openclaw/openclaw.json
   ```

3. **Firewall Configuration**
   ```bash
   # Allow only necessary ports
   ufw allow ssh
   ufw allow [openclaw-port]  # from .env
   ufw enable
   ```

4. **Verify API Key Validity**
   - Test Anthropic API key
   - Test OpenAI API key
   - Test other service integrations

5. **Secure File Permissions**
   ```bash
   chmod 600 /docker/openclaw-r8v9/.env
   chmod 600 /docker/openclaw-r8v9/data/.openclaw/openclaw.json
   ```

6. **Delete Unencrypted Backups**
   ```bash
   # On source server
   rm /root/openclaw-backups/my-migration-backup.tar.gz

   # On target server after successful migration
   rm /root/my-migration-backup.tar.gz.enc
   ```

### Network Security

```bash
# Check gateway bind address
# In openclaw.json, ensure gateway.bind is set appropriately:
# - "loopback" = localhost only
# - "0.0.0.0" = all interfaces (use with caution)
```

### Audit Logs

Keep track of the migration:
```bash
# Create migration log
cat > /root/migration-log.txt <<EOF
Migration Date: $(date)
Source Server: [source-hostname]
Target Server: $(hostname)
OpenClaw Version: $(docker exec openclaw-r8v9-openclaw-1 openclaw --version)
Backup Used: my-migration-backup
Status: Success
Notes: [Add any issues or notes]
EOF
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs

# Check Docker daemon
systemctl status docker

# Verify docker-compose.yml syntax
docker compose config

# Check port conflicts
netstat -tuln | grep [PORT]
```

### Permission Errors

```bash
# Fix data directory permissions
chown -R 1000:1000 /docker/openclaw-r8v9/data

# Fix configuration file permissions
chmod 600 /docker/openclaw-r8v9/.env
chmod -R 755 /docker/openclaw-r8v9/data/.openclaw
```

### API Key Issues

```bash
# Verify keys are set correctly
grep -E "API_KEY|TOKEN" /docker/openclaw-r8v9/.env

# Test Anthropic API
curl https://api.anthropic.com/v1/models \
  -H "x-api-key: YOUR_KEY" \
  -H "anthropic-version: 2023-06-01"
```

### Gateway Not Accessible

```bash
# Check if service is listening
netstat -tuln | grep [PORT]

# Check gateway configuration
jq '.gateway' /docker/openclaw-r8v9/data/.openclaw/openclaw.json

# Test locally
curl http://localhost:[PORT]/health
```

### Workspace Issues

```bash
# Check workspace path
jq -r '.agents.defaults.workspace' /docker/openclaw-r8v9/data/.openclaw/openclaw.json

# Verify workspace exists and is accessible
ls -la /docker/openclaw-r8v9/data/.openclaw/workspace

# Check disk space
df -h /docker
```

## Rollback Procedure

If migration fails:

1. **Stop new server containers:**
   ```bash
   cd /docker/openclaw-r8v9
   docker compose down
   ```

2. **Restore from existing backup on source server:**
   The source server still has the original installation

3. **Document issues for troubleshooting:**
   ```bash
   docker compose logs > /root/migration-error-logs.txt
   ```

## Additional Tips

1. **Schedule Migration During Low Activity:**
   - Plan for maintenance window
   - Notify users of potential downtime

2. **Keep Both Servers Running Initially:**
   - Don't decommission source server immediately
   - Run both in parallel for a few days if possible

3. **Monitor Performance:**
   ```bash
   # CPU and memory
   docker stats

   # Disk usage
   du -sh /docker/openclaw-r8v9/data/.openclaw/workspace
   ```

4. **Regular Backups:**
   - Set up automated backups on new server
   - Test restore procedure periodically

## Support Resources

- OpenClaw Documentation: [relevant links]
- Docker Documentation: https://docs.docker.com
- Claude API Documentation: https://docs.anthropic.com

## Migration Checklist

- [ ] Backup created and verified
- [ ] Backup transferred to new server
- [ ] Prerequisites installed on new server
- [ ] Restore completed successfully
- [ ] Configuration reviewed and updated
- [ ] Containers started successfully
- [ ] Verification script passed
- [ ] Manual functionality tests passed
- [ ] Security measures applied
- [ ] Firewall configured
- [ ] Unencrypted backups deleted
- [ ] Migration documented
- [ ] Source server kept as fallback (temporary)

---

**Migration Complete!**

Remember to monitor the new installation for a few days and keep the source server as a fallback until you're confident everything is working correctly.

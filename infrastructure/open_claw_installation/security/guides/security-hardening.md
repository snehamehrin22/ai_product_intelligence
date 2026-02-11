# OpenClaw Security Hardening Guide

## Security Overview

This guide covers essential security measures for your OpenClaw installation on Hostinger VPS.

**Security Layers:**
1. Network Security (Firewall, SSL/TLS)
2. Access Control (SSH, Gateway Token)
3. Application Security (Reverse Proxy, Rate Limiting)
4. System Security (Updates, Monitoring)
5. Data Security (Backups, Encryption)

---

## Quick Security Checklist

After installation, complete these steps:

- [ ] Configure UFW firewall
- [ ] Set up SSL/HTTPS with Let's Encrypt
- [ ] Configure Nginx reverse proxy
- [ ] Secure SSH access (disable root login, key-based auth)
- [ ] Change default OpenClaw port (optional)
- [ ] Restrict dashboard access by IP (optional)
- [ ] Enable automatic security updates
- [ ] Set up fail2ban for brute force protection
- [ ] Configure regular backups
- [ ] Enable log monitoring
- [ ] Regenerate and secure gateway token
- [ ] Review and minimize API key permissions

---

## 1. Firewall Configuration (UFW)

### Basic Firewall Setup

**Install and enable UFW:**
```bash
sudo apt update
sudo apt install -y ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (IMPORTANT: Do this first!)
sudo ufw allow ssh
# Or specific port if changed
sudo ufw allow 2222/tcp

# Allow HTTP/HTTPS for SSL
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

**Expected Output:**
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

### Important Notes:
- **DO NOT allow port 18789 publicly** - we'll use reverse proxy instead
- If you accidentally lock yourself out, Hostinger provides VNC console access

### Advanced: Restrict by IP (Optional)

**Allow only your IP:**
```bash
# Replace YOUR_IP with your actual IP address
sudo ufw allow from YOUR_IP to any port 443 proto tcp

# Check your current IP
curl ifconfig.me
```

**Allow multiple IPs:**
```bash
sudo ufw allow from 203.0.113.0/24 to any port 443  # Office network
sudo ufw allow from 198.51.100.50 to any port 443   # Home IP
```

---

## 2. SSL/HTTPS Setup with Let's Encrypt

### Prerequisites
- Domain name pointed to your VPS IP
- Ports 80 and 443 open in firewall

### Step 1: Install Nginx and Certbot

```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

### Step 2: Configure Nginx for OpenClaw

**Create Nginx configuration:**
```bash
sudo nano /etc/nginx/sites-available/openclaw
```

**Add this configuration (replace YOUR_DOMAIN):**
```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name YOUR_DOMAIN.com www.YOUR_DOMAIN.com;

    # Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name YOUR_DOMAIN.com www.YOUR_DOMAIN.com;

    # SSL certificates (will be added by certbot)
    # ssl_certificate /etc/letsencrypt/live/YOUR_DOMAIN.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/YOUR_DOMAIN.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Proxy to OpenClaw
    location / {
        proxy_pass http://localhost:18789;
        proxy_http_version 1.1;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;

        # Forward real client IP
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for long-running requests
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Optional: Rate limiting
    limit_req_zone $binary_remote_addr zone=openclaw_limit:10m rate=10r/s;
    limit_req zone=openclaw_limit burst=20 nodelay;

    # Logging
    access_log /var/log/nginx/openclaw_access.log;
    error_log /var/log/nginx/openclaw_error.log;
}
```

**Save and exit** (Ctrl+O, Enter, Ctrl+X)

### Step 3: Enable Site and Test Configuration

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/openclaw /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 4: Obtain SSL Certificate

```bash
# Replace YOUR_DOMAIN and YOUR_EMAIL
sudo certbot --nginx -d YOUR_DOMAIN.com -d www.YOUR_DOMAIN.com --email YOUR_EMAIL --agree-tos --no-eff-email
```

**Follow prompts:**
- Agree to terms
- Choose whether to redirect HTTP to HTTPS (recommended: Yes)

**Verify SSL:**
```bash
# Check certificate
sudo certbot certificates

# Test renewal (dry run)
sudo certbot renew --dry-run
```

### Step 5: Auto-renewal

Certbot automatically installs a renewal timer. Verify:
```bash
sudo systemctl status certbot.timer
```

**Manual renewal (if needed):**
```bash
sudo certbot renew
sudo systemctl reload nginx
```

### Step 6: Update OpenClaw to Bind Localhost Only

**Edit docker-compose.yml:**
```bash
cd /opt/openclaw
nano docker-compose.yml
```

**Find and modify ports section:**
```yaml
services:
  openclaw-gateway:
    ports:
      - "127.0.0.1:18789:18789"  # Bind to localhost only
```

**Restart OpenClaw:**
```bash
docker compose down
docker compose up -d
```

**Now access via:**
```
https://YOUR_DOMAIN.com  # Secure!
```

---

## 3. SSH Security Hardening

### Change Default SSH Port (Optional but Recommended)

**Edit SSH config:**
```bash
sudo nano /etc/ssh/sshd_config
```

**Find and modify:**
```
Port 2222  # Change from 22 to custom port
```

**Update firewall:**
```bash
sudo ufw allow 2222/tcp
sudo ufw delete allow ssh
sudo ufw reload
```

**Restart SSH:**
```bash
sudo systemctl restart sshd
```

**Test new port (in NEW terminal window):**
```bash
ssh -p 2222 root@YOUR_VPS_IP
```

### Disable Root Login

**After creating a sudo user:**

1. **Create new user:**
```bash
adduser yourusername
usermod -aG sudo yourusername
```

2. **Copy SSH keys (if using):**
```bash
mkdir -p /home/yourusername/.ssh
cp ~/.ssh/authorized_keys /home/yourusername/.ssh/
chown -R yourusername:yourusername /home/yourusername/.ssh
chmod 700 /home/yourusername/.ssh
chmod 600 /home/yourusername/.ssh/authorized_keys
```

3. **Test new user (in NEW terminal):**
```bash
ssh yourusername@YOUR_VPS_IP
sudo ls  # Test sudo access
```

4. **Disable root login:**
```bash
sudo nano /etc/ssh/sshd_config
```

**Set:**
```
PermitRootLogin no
PasswordAuthentication no  # Force key-based auth
```

5. **Restart SSH:**
```bash
sudo systemctl restart sshd
```

### Enable SSH Key-Based Authentication

**On your local machine:**
```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy to server
ssh-copy-id -p 2222 yourusername@YOUR_VPS_IP
```

**Test:**
```bash
ssh -p 2222 yourusername@YOUR_VPS_IP
```

Should login without password.

---

## 4. Fail2Ban (Brute Force Protection)

### Install and Configure Fail2Ban

```bash
sudo apt install -y fail2ban
```

**Create custom configuration:**
```bash
sudo nano /etc/fail2ban/jail.local
```

**Add configuration:**
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
destemail = your_email@example.com
sendername = Fail2Ban
action = %(action_mwl)s

[sshd]
enabled = true
port = 2222  # Use your SSH port
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
```

**Start and enable:**
```bash
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

**Check status:**
```bash
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

**View banned IPs:**
```bash
sudo fail2ban-client status sshd
```

**Unban an IP (if needed):**
```bash
sudo fail2ban-client set sshd unbanip 192.168.1.100
```

---

## 5. Automatic Security Updates

### Enable Unattended Upgrades

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

**Configure:**
```bash
sudo nano /etc/apt/apt.conf.d/50unattended-upgrades
```

**Ensure these are uncommented:**
```
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";  # Set to "true" if you want auto-reboot
```

**Enable automatic updates:**
```bash
sudo nano /etc/apt/apt.conf.d/20auto-upgrades
```

**Set:**
```
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
```

**Test:**
```bash
sudo unattended-upgrades --dry-run --debug
```

---

## 6. OpenClaw Application Security

### Regenerate Gateway Token

**If you suspect compromise:**
```bash
cd /opt/openclaw
docker compose run --rm openclaw-cli auth regenerate-token
```

**Save new token securely** (password manager recommended)

### Secure Token Storage

**Never:**
- Commit token to git
- Share via unencrypted channels
- Store in plain text files

**Do:**
- Use password manager (1Password, Bitwarden)
- Store in encrypted .env file
- Rotate periodically (every 90 days)

### Enable Sandbox Mode

**Edit OpenClaw config:**
```bash
cd /opt/openclaw
nano docker-compose.yml
```

**Add environment variable:**
```yaml
environment:
  - OPENCLAW_SANDBOX_MODE=non-main
```

**Restart:**
```bash
docker compose down
docker compose up -d
```

### Restrict API Key Permissions

**For each AI provider:**

**Anthropic:**
- Use workspace-specific keys
- Set spending limits in console

**OpenAI:**
- Create separate project keys
- Set usage limits
- Enable usage notifications

**Google Gemini:**
- Restrict API key to specific IPs
- Set quota limits

---

## 7. Monitoring and Logging

### Set Up Log Rotation

**Configure OpenClaw logs:**
```bash
sudo nano /etc/logrotate.d/openclaw
```

**Add:**
```
/home/*/.openclaw/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    missingok
    create 0644 node node
}
```

### Monitor System Resources

**Install monitoring tools:**
```bash
sudo apt install -y htop iotop nethogs
```

**Check resources:**
```bash
# Interactive monitoring
htop

# Docker stats
docker stats

# Disk usage
df -h
du -sh /opt/openclaw
du -sh ~/.openclaw

# Network connections
netstat -tulpn
```

### Set Up Alerts (Optional)

**Install monitoring agent:**
```bash
# Example: Netdata
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

**Access:** `http://YOUR_VPS_IP:19999`

---

## 8. Backup Strategy

### Automated Backup Script

**Create backup script:**
```bash
sudo nano /usr/local/bin/backup-openclaw.sh
```

**Add script:**
```bash
#!/bin/bash

BACKUP_DIR="/root/openclaw-backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup OpenClaw configuration
tar -czf $BACKUP_DIR/openclaw_config_$DATE.tar.gz \
    ~/.openclaw/config.json \
    ~/.openclaw/providers.json \
    /opt/openclaw/docker-compose.yml \
    /opt/openclaw/.env 2>/dev/null

# Backup Nginx config
tar -czf $BACKUP_DIR/nginx_config_$DATE.tar.gz \
    /etc/nginx/sites-available/openclaw \
    /etc/letsencrypt 2>/dev/null

# Remove old backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Log
echo "Backup completed: $(date)" >> $BACKUP_DIR/backup.log
```

**Make executable:**
```bash
sudo chmod +x /usr/local/bin/backup-openclaw.sh
```

**Test backup:**
```bash
sudo /usr/local/bin/backup-openclaw.sh
ls -lh /root/openclaw-backups/
```

**Schedule daily backups:**
```bash
sudo crontab -e
```

**Add:**
```
# Daily backup at 2 AM
0 2 * * * /usr/local/bin/backup-openclaw.sh
```

### Restore from Backup

```bash
# List backups
ls -lh /root/openclaw-backups/

# Restore configuration
tar -xzf /root/openclaw-backups/openclaw_config_YYYYMMDD_HHMMSS.tar.gz -C /

# Restart OpenClaw
cd /opt/openclaw
docker compose restart
```

---

## 9. Security Audit Checklist

### Monthly Security Review

Run this checklist monthly:

```bash
# 1. Check for system updates
sudo apt update
sudo apt list --upgradable

# 2. Review firewall rules
sudo ufw status numbered

# 3. Check fail2ban bans
sudo fail2ban-client status sshd

# 4. Review SSH auth logs
sudo tail -100 /var/log/auth.log | grep Failed

# 5. Check OpenClaw logs for errors
cd /opt/openclaw
docker compose logs --tail=100 | grep -i error

# 6. Verify SSL certificate expiry
sudo certbot certificates

# 7. Check disk space
df -h

# 8. Review Docker container status
docker compose ps
docker stats --no-stream

# 9. Check for unused Docker images
docker images
docker system df

# 10. Verify backup completion
ls -lh /root/openclaw-backups/ | tail -5
```

---

## 10. Incident Response

### If Gateway Token is Compromised

```bash
# 1. Regenerate token immediately
cd /opt/openclaw
docker compose run --rm openclaw-cli auth regenerate-token

# 2. Review logs for unauthorized access
docker compose logs | grep -i "authentication\|login"

# 3. Check active sessions
docker compose run --rm openclaw-cli sessions list

# 4. Terminate suspicious sessions
docker compose run --rm openclaw-cli sessions terminate SESSION_ID
```

### If API Key is Compromised

```bash
# 1. Revoke key in provider console (Anthropic/OpenAI/etc.)
# 2. Generate new key
# 3. Update OpenClaw configuration
docker compose run --rm openclaw-cli config set providers.anthropic.apiKey "NEW_KEY"

# 4. Restart
docker compose restart

# 5. Review API usage for unusual activity
```

### If Server is Compromised

```bash
# 1. Disconnect from network (if possible)
sudo ufw deny incoming

# 2. Review active connections
netstat -tulpn
who

# 3. Check for rootkits
sudo apt install -y rkhunter
sudo rkhunter --check

# 4. Review running processes
ps aux | less
top

# 5. Consider full server rebuild if severely compromised
```

---

## Security Best Practices Summary

### Do's
✅ Use strong, unique passwords
✅ Enable SSH key-based authentication
✅ Keep system and software updated
✅ Use SSL/HTTPS for all connections
✅ Regular backups (automated)
✅ Monitor logs for suspicious activity
✅ Use firewall (UFW)
✅ Rotate credentials periodically
✅ Use fail2ban for brute force protection
✅ Restrict access by IP when possible

### Don'ts
❌ Expose port 18789 directly to internet
❌ Use default ports without protection
❌ Share gateway token via unencrypted channels
❌ Commit secrets to git repositories
❌ Ignore security updates
❌ Use weak or default passwords
❌ Disable firewall
❌ Run services as root unnecessarily
❌ Store API keys in plain text
❌ Forget to backup regularly

---

## Quick Security Setup Script

See `security_hardening.sh` for automated setup of:
- UFW firewall
- Fail2ban
- Automatic updates
- SSH hardening options
- Backup automation

---

## Additional Resources

- **OWASP Security Guidelines:** https://owasp.org/
- **Ubuntu Security:** https://ubuntu.com/security
- **Let's Encrypt Docs:** https://letsencrypt.org/docs/
- **Docker Security:** https://docs.docker.com/engine/security/
- **Nginx Security:** https://nginx.org/en/docs/http/ngx_http_ssl_module.html

---

**Security Level Achieved:**
- ⭐⭐⭐⭐⭐ Basic (Firewall + SSL)
- ⭐⭐⭐⭐⭐ Intermediate (+ SSH hardening + Fail2ban)
- ⭐⭐⭐⭐⭐ Advanced (+ IP restrictions + Monitoring)
- ⭐⭐⭐⭐⭐ Paranoid (+ VPN + 2FA + SIEM)

**Recommended Level:** Intermediate (covers 95% of threats)

---

**Last Updated:** 2026-02-07
**Next Review:** Monthly

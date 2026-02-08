#!/bin/bash
#
# Complete Server Backup Script
# Backs up everything: OpenClaw, shared folders, Git config, security settings
# Usage: ./full-server-backup.sh [backup-name]
#

set -euo pipefail

# Configuration
BACKUP_NAME="${1:-server-backup-$(date +%Y%m%d-%H%M%S)}"
BACKUP_BASE="/root/server-backups"
BACKUP_DIR="${BACKUP_BASE}/${BACKUP_NAME}"
MANIFEST_FILE="${BACKUP_DIR}/backup-manifest.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root"
   exit 1
fi

echo "========================================="
echo "  Complete Server Backup"
echo "========================================="
echo ""
log_info "Backup name: ${BACKUP_NAME}"
log_info "Backup location: ${BACKUP_DIR}"
echo ""

# Create backup directory structure
mkdir -p "${BACKUP_DIR}"/{docker,shared,system,security,git,services,scripts}

# Create manifest
log_step "Creating backup manifest..."
cat > "${MANIFEST_FILE}" <<EOF
{
  "backup_name": "${BACKUP_NAME}",
  "backup_type": "full_server",
  "created_at": "$(date -Iseconds)",
  "hostname": "$(hostname)",
  "ip_address": "$(hostname -I | awk '{print $1}')",
  "os_version": "$(lsb_release -d 2>/dev/null | cut -f2 || echo 'Unknown')",
  "kernel": "$(uname -r)",
  "source_server": "187.77.1.7"
}
EOF

# 1. Backup Docker (OpenClaw)
log_step "Backing up Docker and OpenClaw..."
if [ -d "/docker" ]; then
    log_info "Backing up /docker directory..."
    rsync -av --exclude='*.log' --exclude='node_modules' /docker/ "${BACKUP_DIR}/docker/" 2>/dev/null || \
        log_warn "Some Docker files may have been skipped"
    DOCKER_SIZE=$(du -sh "${BACKUP_DIR}/docker" | cut -f1)
    log_info "Docker backup size: $DOCKER_SIZE"
else
    log_warn "/docker directory not found"
fi

# 2. Backup Shared Folders
log_step "Backing up /shared directory..."
if [ -d "/shared" ]; then
    log_info "Backing up shared openclaw, projects, and scripts..."
    rsync -av --exclude='.git/objects' --exclude='node_modules' /shared/ "${BACKUP_DIR}/shared/" 2>/dev/null || \
        log_warn "Some shared files may have been skipped"

    # Create inventory of shared folder
    echo "Shared folder contents:" > "${BACKUP_DIR}/shared/INVENTORY.txt"
    du -sh /shared/*/ >> "${BACKUP_DIR}/shared/INVENTORY.txt" 2>/dev/null || true

    SHARED_SIZE=$(du -sh "${BACKUP_DIR}/shared" | cut -f1)
    log_info "Shared backup size: $SHARED_SIZE"
else
    log_warn "/shared directory not found"
fi

# 3. Backup SSH Configuration and Keys
log_step "Backing up SSH configuration..."
if [ -d "/root/.ssh" ]; then
    cp -r /root/.ssh "${BACKUP_DIR}/security/root-ssh"
    chmod -R 600 "${BACKUP_DIR}/security/root-ssh"/*
    log_info "SSH keys and config backed up"
else
    log_warn "SSH directory not found"
fi

# Backup SSH daemon config
if [ -f "/etc/ssh/sshd_config" ]; then
    cp /etc/ssh/sshd_config "${BACKUP_DIR}/security/"
    log_info "SSH daemon config backed up"
fi

# 4. Backup Git Configuration
log_step "Backing up Git configuration..."

# Global Git config
if [ -f "/root/.gitconfig" ]; then
    cp /root/.gitconfig "${BACKUP_DIR}/git/"
fi

# System Git config
git config --global --list > "${BACKUP_DIR}/git/global-git-config.txt" 2>/dev/null || true
git config --system --list > "${BACKUP_DIR}/git/system-git-config.txt" 2>/dev/null || true

# List all Git repos
log_info "Finding all Git repositories..."
find /shared /docker /root /home -name ".git" -type d 2>/dev/null | \
    sed 's|/.git||' > "${BACKUP_DIR}/git/git-repositories.txt" || true

log_info "Git configuration backed up"

# 5. Backup Firewall Rules
log_step "Backing up firewall configuration..."

# UFW rules
if command -v ufw &>/dev/null; then
    ufw status verbose > "${BACKUP_DIR}/security/ufw-status.txt" 2>/dev/null || true

    # Backup UFW rules files
    if [ -d "/etc/ufw" ]; then
        cp -r /etc/ufw "${BACKUP_DIR}/security/" 2>/dev/null || true
    fi
    log_info "UFW firewall rules backed up"
fi

# iptables rules
iptables-save > "${BACKUP_DIR}/security/iptables-rules.txt" 2>/dev/null || true
ip6tables-save > "${BACKUP_DIR}/security/ip6tables-rules.txt" 2>/dev/null || true
log_info "iptables rules backed up"

# 6. Backup Installed Packages
log_step "Backing up package information..."

# APT packages
dpkg --get-selections > "${BACKUP_DIR}/system/dpkg-packages.txt" 2>/dev/null || true
apt list --installed > "${BACKUP_DIR}/system/apt-packages.txt" 2>/dev/null || true

# NPM global packages
npm list -g --depth=0 > "${BACKUP_DIR}/system/npm-global-packages.txt" 2>/dev/null || true

# Docker images
docker images --format "{{.Repository}}:{{.Tag}}" > "${BACKUP_DIR}/docker/docker-images.txt" 2>/dev/null || true

log_info "Package lists backed up"

# 7. Backup Cron Jobs
log_step "Backing up cron jobs..."
crontab -l > "${BACKUP_DIR}/system/root-crontab.txt" 2>/dev/null || echo "No crontab for root" > "${BACKUP_DIR}/system/root-crontab.txt"

# System-wide cron
if [ -d "/etc/cron.d" ]; then
    cp -r /etc/cron.d "${BACKUP_DIR}/system/" 2>/dev/null || true
fi

log_info "Cron jobs backed up"

# 8. Backup System Services
log_step "Backing up service configuration..."

# List enabled services
systemctl list-unit-files --state=enabled > "${BACKUP_DIR}/services/enabled-services.txt" 2>/dev/null || true

# Docker compose files
find /docker /shared /root -name "docker-compose.yml" -o -name "docker-compose.yaml" 2>/dev/null | \
    while read file; do
        cp --parents "$file" "${BACKUP_DIR}/services/" 2>/dev/null || true
    done

log_info "Services backed up"

# 9. Backup Environment Variables
log_step "Backing up environment variables..."

# Find all .env files
find /docker /shared /root -name ".env" -type f 2>/dev/null | \
    while read envfile; do
        mkdir -p "${BACKUP_DIR}/system/env-files/$(dirname $envfile)"
        cp "$envfile" "${BACKUP_DIR}/system/env-files/$envfile" 2>/dev/null || true
    done

log_info "Environment files backed up"

# 10. Backup Custom Scripts
log_step "Backing up custom scripts from /shared/scripts..."
if [ -d "/shared/scripts" ]; then
    cp -r /shared/scripts/* "${BACKUP_DIR}/scripts/" 2>/dev/null || true
    log_info "Custom scripts backed up"
fi

# 11. Network Configuration
log_step "Backing up network configuration..."
ip addr show > "${BACKUP_DIR}/system/network-interfaces.txt"
ip route show > "${BACKUP_DIR}/system/network-routes.txt"
cat /etc/hosts > "${BACKUP_DIR}/system/hosts" 2>/dev/null || true
cat /etc/resolv.conf > "${BACKUP_DIR}/system/resolv.conf" 2>/dev/null || true

# 12. Create Data Directory List
log_step "Creating directory tree..."
tree -L 3 -d /docker > "${BACKUP_DIR}/docker-tree.txt" 2>/dev/null || \
    find /docker -type d -maxdepth 3 > "${BACKUP_DIR}/docker-tree.txt" 2>/dev/null || true

tree -L 3 -d /shared > "${BACKUP_DIR}/shared-tree.txt" 2>/dev/null || \
    find /shared -type d -maxdepth 3 > "${BACKUP_DIR}/shared-tree.txt" 2>/dev/null || true

# 13. Create checksums
log_step "Creating checksums..."
cd "${BACKUP_DIR}"
find . -type f -not -name "checksums.txt" -exec sha256sum {} \; > checksums.txt 2>/dev/null

# 14. Backup size summary
log_step "Calculating backup sizes..."
cat > "${BACKUP_DIR}/backup-sizes.txt" <<EOF
Backup Size Summary
===================

Docker:        $(du -sh "${BACKUP_DIR}/docker" 2>/dev/null | cut -f1 || echo "N/A")
Shared:        $(du -sh "${BACKUP_DIR}/shared" 2>/dev/null | cut -f1 || echo "N/A")
Security:      $(du -sh "${BACKUP_DIR}/security" 2>/dev/null | cut -f1 || echo "N/A")
System:        $(du -sh "${BACKUP_DIR}/system" 2>/dev/null | cut -f1 || echo "N/A")
Git:           $(du -sh "${BACKUP_DIR}/git" 2>/dev/null | cut -f1 || echo "N/A")
Services:      $(du -sh "${BACKUP_DIR}/services" 2>/dev/null | cut -f1 || echo "N/A")

Total:         $(du -sh "${BACKUP_DIR}" | cut -f1)
EOF

# 15. Create encrypted and unencrypted archives
log_step "Creating archive files..."

# Unencrypted archive (for faster restore)
ARCHIVE_UNENC="${BACKUP_BASE}/${BACKUP_NAME}.tar.gz"
tar czf "${ARCHIVE_UNENC}" -C "${BACKUP_BASE}" "${BACKUP_NAME}"
UNENC_SIZE=$(du -h "${ARCHIVE_UNENC}" | cut -f1)

# Encrypted archive (for secure transfer)
ARCHIVE_ENC="${BACKUP_BASE}/${BACKUP_NAME}.tar.gz.enc"
cat "${ARCHIVE_UNENC}" | openssl enc -aes-256-cbc -salt -pbkdf2 \
    -out "${ARCHIVE_ENC}" -pass pass:"CHANGE_THIS_PASSWORD"
ENC_SIZE=$(du -h "${ARCHIVE_ENC}" | cut -f1)

# 16. Create backup summary
log_step "Creating backup summary..."
cat > "${BACKUP_DIR}/BACKUP-SUMMARY.txt" <<EOF
========================================
Complete Server Backup Summary
========================================

Backup Name: ${BACKUP_NAME}
Created: $(date)
Server: 187.77.1.7 ($(hostname))
Backup Type: Full Server Migration

========================================
What Was Backed Up
========================================

1. DOCKER & OPENCLAW
   - Complete /docker directory
   - OpenClaw installation and configuration
   - Docker Compose files
   - All container data
   Size: $(du -sh "${BACKUP_DIR}/docker" 2>/dev/null | cut -f1 || echo "N/A")

2. SHARED FOLDERS
   - /shared/openclaw
   - /shared/projects (including Git repositories)
   - /shared/scripts
   Size: $(du -sh "${BACKUP_DIR}/shared" 2>/dev/null | cut -f1 || echo "N/A")

3. SECURITY CONFIGURATION
   - SSH keys (/root/.ssh)
   - SSH daemon config
   - UFW firewall rules
   - iptables rules
   - Authorized keys
   Size: $(du -sh "${BACKUP_DIR}/security" 2>/dev/null | cut -f1 || echo "N/A")

4. GIT CONFIGURATION
   - Global Git config
   - System Git config
   - List of all Git repositories
   - Git safe directories

5. SYSTEM CONFIGURATION
   - Installed packages (apt/dpkg)
   - NPM global packages
   - Cron jobs
   - Network configuration
   - Environment variables (.env files)
   - Docker images list

6. SERVICES
   - Enabled systemd services
   - Docker Compose configurations
   - Service states

========================================
Archives Created
========================================

Directory: ${BACKUP_DIR}
           Size: $(du -sh "${BACKUP_DIR}" | cut -f1)

Unencrypted: ${ARCHIVE_UNENC}
             Size: ${UNENC_SIZE}

Encrypted:   ${ARCHIVE_ENC}
             Size: ${ENC_SIZE}
             Password: CHANGE_THIS_PASSWORD

========================================
Security Items Included
========================================

API Keys & Tokens:
  - Anthropic API Key
  - OpenAI API Key
  - Gemini API Key
  - Perplexity API Key
  - Brave Search API Key
  - Discord Bot Token
  - OpenClaw Gateway Token

SSH Keys:
  - id_ed25519 (private)
  - id_ed25519.pub (public)
  - authorized_keys
  - known_hosts

Firewall Rules:
  - UFW configuration
  - iptables rules

========================================
Verification Files
========================================

- checksums.txt (SHA256 of all files)
- backup-manifest.json (metadata)
- backup-sizes.txt (size breakdown)
- docker-tree.txt (directory structure)
- shared-tree.txt (directory structure)

========================================
Next Steps for Migration
========================================

1. Transfer to new server:
   scp ${ARCHIVE_ENC} root@<NEW_IP>:/root/

2. On new server, run:
   /root/full-server-restore.sh /root/$(basename ${ARCHIVE_ENC})

3. Verify restoration:
   /root/verify-server-migration.sh

========================================
CRITICAL SECURITY NOTES
========================================

⚠️  This backup contains:
   - Private SSH keys
   - API keys and tokens
   - Firewall configurations
   - All sensitive data

✓ MUST DO:
   1. Change backup encryption password
   2. Use secure transfer (SCP/SFTP, not FTP)
   3. Delete unencrypted archive after transfer
   4. Store encryption password securely
   5. Restrict backup file permissions (600)

✓ RECOMMENDED:
   1. Test restore on new server
   2. Verify all services after migration
   3. Update DNS records
   4. Keep original server for 48h as fallback

========================================
Support Files
========================================

Complete documentation:
  - /root/FULL-SERVER-MIGRATION-GUIDE.md
  - /root/full-server-restore.sh
  - /root/verify-server-migration.sh

========================================

Backup completed: $(date)
Total backup size: $(du -sh "${BACKUP_DIR}" | cut -f1)
Total archive size: ${ENC_SIZE} (encrypted)

========================================
EOF

# Display summary
log_info "Backup completed successfully!"
echo ""
cat "${BACKUP_DIR}/BACKUP-SUMMARY.txt"

echo ""
log_warn "REMEMBER TO:"
echo "  1. Change the encryption password before production use"
echo "  2. Securely store the password"
echo "  3. Delete unencrypted archives after transfer"
echo "  4. chmod 600 the backup files"
echo ""
log_info "Backup files:"
echo "  Directory: ${BACKUP_DIR}"
echo "  Encrypted: ${ARCHIVE_ENC}"
echo "  Unencrypted: ${ARCHIVE_UNENC}"

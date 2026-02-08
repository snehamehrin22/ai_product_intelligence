#!/bin/bash
#
# Complete Server Restore Script
# Restores everything: OpenClaw, shared folders, Git config, security settings
# Usage: ./full-server-restore.sh [backup-archive-file]
#

set -euo pipefail

# Colors
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

# Get archive file
ARCHIVE_FILE="${1:-}"
if [ -z "$ARCHIVE_FILE" ]; then
    log_error "Usage: $0 <backup-archive-file>"
    echo "Example: $0 /root/server-backup-20260208-120000.tar.gz.enc"
    exit 1
fi

if [ ! -f "$ARCHIVE_FILE" ]; then
    log_error "Archive file not found: $ARCHIVE_FILE"
    exit 1
fi

echo "========================================="
echo "  Complete Server Restore"
echo "========================================="
echo ""
log_info "Restoring from: $ARCHIVE_FILE"
echo ""

# Create temporary restore directory
RESTORE_DIR="/tmp/server-restore-$(date +%s)"
mkdir -p "$RESTORE_DIR"
cd "$RESTORE_DIR"

# Extract archive
if [[ "$ARCHIVE_FILE" == *.enc ]]; then
    log_step "Decrypting and extracting archive..."
    read -sp "Enter backup password: " BACKUP_PASSWORD
    echo
    openssl enc -aes-256-cbc -d -pbkdf2 -in "$ARCHIVE_FILE" -pass pass:"$BACKUP_PASSWORD" | tar xzf -
else
    log_step "Extracting archive..."
    tar xzf "$ARCHIVE_FILE"
fi

# Find backup directory
BACKUP_NAME=$(ls -1 | head -1)
BACKUP_PATH="$RESTORE_DIR/$BACKUP_NAME"

if [ ! -d "$BACKUP_PATH" ]; then
    log_error "Backup directory not found in archive"
    exit 1
fi

log_info "Found backup: $BACKUP_NAME"
echo ""

# Display backup summary
if [ -f "$BACKUP_PATH/BACKUP-SUMMARY.txt" ]; then
    cat "$BACKUP_PATH/BACKUP-SUMMARY.txt"
    echo ""
fi

# Verify checksums
log_step "Verifying backup integrity..."
cd "$BACKUP_PATH"
if [ -f "checksums.txt" ]; then
    if sha256sum -c checksums.txt --quiet 2>/dev/null; then
        log_info "✓ Checksum verification passed"
    else
        log_warn "⚠ Checksum verification failed"
        read -p "Continue anyway? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            log_error "Restore cancelled"
            exit 1
        fi
    fi
fi

echo ""
log_warn "This will restore the complete server configuration!"
log_warn "Existing files may be overwritten!"
echo ""
read -p "Continue with full restore? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    log_error "Restore cancelled"
    exit 1
fi

# 1. Restore Docker & OpenClaw
echo ""
log_step "Restoring Docker and OpenClaw..."
if [ -d "$BACKUP_PATH/docker" ]; then
    mkdir -p /docker
    rsync -av "$BACKUP_PATH/docker/" /docker/
    log_info "✓ Docker restored"
else
    log_warn "No Docker backup found"
fi

# 2. Restore Shared Folders
log_step "Restoring /shared directory..."
if [ -d "$BACKUP_PATH/shared" ]; then
    mkdir -p /shared
    rsync -av "$BACKUP_PATH/shared/" /shared/
    log_info "✓ Shared folders restored"
else
    log_warn "No shared folder backup found"
fi

# 3. Restore SSH Configuration
log_step "Restoring SSH configuration..."
if [ -d "$BACKUP_PATH/security/root-ssh" ]; then
    mkdir -p /root/.ssh
    cp -r "$BACKUP_PATH/security/root-ssh"/* /root/.ssh/
    chmod 700 /root/.ssh
    chmod 600 /root/.ssh/*
    chmod 644 /root/.ssh/*.pub 2>/dev/null || true
    log_info "✓ SSH keys restored"
fi

if [ -f "$BACKUP_PATH/security/sshd_config" ]; then
    read -p "Restore SSH daemon config? (yes/no): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        cp "$BACKUP_PATH/security/sshd_config" /etc/ssh/sshd_config.new
        log_warn "SSH config saved as /etc/ssh/sshd_config.new"
        log_warn "Review and manually apply if needed"
    fi
fi

# 4. Restore Git Configuration
log_step "Restoring Git configuration..."
if [ -f "$BACKUP_PATH/git/.gitconfig" ]; then
    cp "$BACKUP_PATH/git/.gitconfig" /root/.gitconfig
    log_info "✓ Git config restored"
fi

# Restore Git safe directories
if [ -f "$BACKUP_PATH/git/global-git-config.txt" ]; then
    grep "safe.directory" "$BACKUP_PATH/git/global-git-config.txt" | while read -r line; do
        SAFE_DIR=$(echo "$line" | cut -d'=' -f2)
        git config --global --add safe.directory "$SAFE_DIR" 2>/dev/null || true
    done
    log_info "✓ Git safe directories restored"
fi

# 5. Restore Firewall Rules
log_step "Restoring firewall configuration..."
if [ -f "$BACKUP_PATH/security/ufw-status.txt" ]; then
    log_warn "UFW rules found in backup"
    log_warn "File: $BACKUP_PATH/security/ufw-status.txt"
    read -p "Restore firewall rules now? (yes/no): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        # Install UFW if not present
        if ! command -v ufw &>/dev/null; then
            apt install -y ufw
        fi

        # Copy UFW configuration
        if [ -d "$BACKUP_PATH/security/ufw" ]; then
            cp -r "$BACKUP_PATH/security/ufw"/* /etc/ufw/ 2>/dev/null || true
        fi

        # Enable UFW
        ufw --force enable
        log_info "✓ Firewall restored"
    else
        log_warn "Firewall rules NOT restored - apply manually if needed"
    fi
fi

# 6. Restore Cron Jobs
log_step "Restoring cron jobs..."
if [ -f "$BACKUP_PATH/system/root-crontab.txt" ] && \
   [ "$(cat $BACKUP_PATH/system/root-crontab.txt)" != "No crontab for root" ]; then
    read -p "Restore root crontab? (yes/no): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        crontab "$BACKUP_PATH/system/root-crontab.txt"
        log_info "✓ Crontab restored"
    fi
fi

# 7. Install packages (optional)
log_step "Package installation..."
if [ -f "$BACKUP_PATH/system/dpkg-packages.txt" ]; then
    log_warn "Package list available"
    read -p "Install packages from backup? (yes/no): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Installing packages (this may take a while)..."
        apt update
        dpkg --set-selections < "$BACKUP_PATH/system/dpkg-packages.txt"
        apt-get dselect-upgrade -y
        log_info "✓ Packages installed"
    fi
fi

# 8. Set permissions
log_step "Setting correct permissions..."
chmod 600 /docker/openclaw-r8v9/.env 2>/dev/null || true
chmod 600 /docker/openclaw-r8v9/data/.openclaw/openclaw.json 2>/dev/null || true
chown -R 1000:1000 /docker/openclaw-r8v9/data 2>/dev/null || true
chmod -R g+w /shared 2>/dev/null || true
chgrp -R devs /shared 2>/dev/null || true
log_info "✓ Permissions set"

# 9. Clean up
log_step "Cleaning up temporary files..."
rm -rf "$RESTORE_DIR"

# Summary
echo ""
echo "========================================="
echo "  Restore Complete!"
echo "========================================="
echo ""
log_info "Restored components:"
echo "  ✓ Docker & OpenClaw"
echo "  ✓ Shared folders (/shared)"
echo "  ✓ SSH configuration"
echo "  ✓ Git configuration"
echo ""
log_warn "IMPORTANT: Review these before starting services:"
echo "  1. /docker/openclaw-r8v9/.env (check ports, API keys)"
echo "  2. /etc/ssh/sshd_config.new (if created)"
echo "  3. Firewall rules (ufw status)"
echo ""
log_info "Next steps:"
echo "  1. Review and update configuration files"
echo "  2. Start Docker services:"
echo "     cd /docker/openclaw-r8v9 && docker compose up -d"
echo "  3. Verify installation:"
echo "     /root/verify-server-migration.sh"
echo "  4. Check logs:"
echo "     docker compose logs -f"
echo ""
log_info "Backup files preserved at: $BACKUP_PATH"

#!/bin/bash
#
# OpenClaw Restore Script
# Restores OpenClaw configuration from backup
# Usage: ./openclaw-restore.sh [backup-archive-file]
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root"
   exit 1
fi

# Get archive file
ARCHIVE_FILE="${1:-}"
if [ -z "$ARCHIVE_FILE" ]; then
    log_error "Usage: $0 <backup-archive-file>"
    echo "Example: $0 /root/openclaw-backup-20260208-120000.tar.gz.enc"
    exit 1
fi

if [ ! -f "$ARCHIVE_FILE" ]; then
    log_error "Archive file not found: $ARCHIVE_FILE"
    exit 1
fi

# Configuration
RESTORE_DIR="/tmp/openclaw-restore-$(date +%s)"
TARGET_DIR="/docker/openclaw-r8v9"

log_info "Starting OpenClaw restore from: $ARCHIVE_FILE"
log_warn "This will restore OpenClaw configuration to: $TARGET_DIR"

# Ask for confirmation
read -p "Continue? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    log_error "Restore cancelled by user"
    exit 1
fi

# Create temporary restore directory
mkdir -p "$RESTORE_DIR"
cd "$RESTORE_DIR"

# Detect if encrypted
if [[ "$ARCHIVE_FILE" == *.enc ]]; then
    log_step "Decrypting archive..."
    read -sp "Enter backup password: " BACKUP_PASSWORD
    echo
    openssl enc -aes-256-cbc -d -pbkdf2 -in "$ARCHIVE_FILE" -pass pass:"$BACKUP_PASSWORD" | tar xzf -
else
    log_step "Extracting archive..."
    tar xzf "$ARCHIVE_FILE"
fi

# Find the backup directory
BACKUP_NAME=$(ls -1 | head -1)
BACKUP_PATH="$RESTORE_DIR/$BACKUP_NAME"

if [ ! -d "$BACKUP_PATH" ]; then
    log_error "Backup directory not found in archive"
    exit 1
fi

log_info "Found backup: $BACKUP_NAME"

# Display backup summary
if [ -f "$BACKUP_PATH/BACKUP-SUMMARY.txt" ]; then
    echo ""
    cat "$BACKUP_PATH/BACKUP-SUMMARY.txt"
    echo ""
fi

# Verify checksums
log_step "Verifying backup integrity..."
cd "$BACKUP_PATH"
if [ -f "checksums.txt" ]; then
    if sha256sum -c checksums.txt --quiet 2>/dev/null; then
        log_info "Checksum verification passed"
    else
        log_warn "Checksum verification failed - some files may be corrupted"
        read -p "Continue anyway? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            log_error "Restore cancelled"
            exit 1
        fi
    fi
fi

# Check if OpenClaw is running
log_step "Checking for running OpenClaw containers..."
if docker ps | grep -q openclaw; then
    log_warn "OpenClaw containers are running"
    read -p "Stop containers before restore? (yes/no): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Stopping OpenClaw..."
        cd "$TARGET_DIR" 2>/dev/null && docker compose down || true
    else
        log_error "Please stop OpenClaw manually before restoring"
        exit 1
    fi
fi

# Backup existing installation if it exists
if [ -d "$TARGET_DIR" ]; then
    BACKUP_EXISTING="${TARGET_DIR}.backup-$(date +%Y%m%d-%H%M%S)"
    log_warn "Existing installation found at $TARGET_DIR"
    read -p "Create backup of existing installation? (yes/no): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Backing up existing installation to: $BACKUP_EXISTING"
        cp -r "$TARGET_DIR" "$BACKUP_EXISTING"
    fi
fi

# Create target directory
log_step "Creating target directory structure..."
mkdir -p "$TARGET_DIR/data"

# Restore Docker configuration
log_step "Restoring Docker configuration..."
cp "$BACKUP_PATH/docker/docker-compose.yml" "$TARGET_DIR/"
cp "$BACKUP_PATH/docker/.env" "$TARGET_DIR/"
cp "$BACKUP_PATH/docker/.build.log" "$TARGET_DIR/" 2>/dev/null || true

# Restore OpenClaw configuration
log_step "Restoring OpenClaw configuration..."
cp -r "$BACKUP_PATH/config/.openclaw" "$TARGET_DIR/data/"

# Restore Claude configuration
log_step "Restoring Claude configuration..."
cp "$BACKUP_PATH/config/.claude.json"* "$TARGET_DIR/data/" 2>/dev/null || true
cp -r "$BACKUP_PATH/config/.claude" "$TARGET_DIR/data/" 2>/dev/null || true

# Restore other configuration files
log_step "Restoring additional configuration files..."
cp "$BACKUP_PATH/config/.gitconfig" "$TARGET_DIR/data/" 2>/dev/null || true
cp "$BACKUP_PATH/config/.zshrc" "$TARGET_DIR/data/" 2>/dev/null || true

# Restore projects
if [ -d "$BACKUP_PATH/projects/my-projects" ]; then
    log_step "Restoring projects..."
    cp -r "$BACKUP_PATH/projects/my-projects" "$TARGET_DIR/data/"
fi

# Set correct permissions
log_step "Setting correct permissions..."
chown -R 1000:1000 "$TARGET_DIR/data" 2>/dev/null || true

# Clean up temporary files
log_step "Cleaning up temporary files..."
rm -rf "$RESTORE_DIR"

log_info "Restore completed successfully!"
echo ""
log_warn "IMPORTANT: Next steps:"
echo "1. Review the configuration files, especially:"
echo "   - $TARGET_DIR/.env (API keys and tokens)"
echo "   - $TARGET_DIR/docker-compose.yml (ports and volumes)"
echo "   - $TARGET_DIR/data/.openclaw/openclaw.json (OpenClaw settings)"
echo ""
echo "2. Update any server-specific settings (hostname, IP, etc.)"
echo ""
echo "3. Start OpenClaw:"
echo "   cd $TARGET_DIR && docker compose up -d"
echo ""
echo "4. Check container status:"
echo "   docker compose logs -f"
echo ""
echo "5. Run verification script:"
echo "   ./openclaw-verify.sh"
echo ""
log_info "Configuration restored to: $TARGET_DIR"

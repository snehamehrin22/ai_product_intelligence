#!/bin/bash
#
# OpenClaw Complete Backup Script
# Creates a comprehensive backup of OpenClaw configuration and data
# Usage: ./openclaw-backup.sh [backup-name]
#

set -euo pipefail

# Configuration
OPENCLAW_DIR="/docker/openclaw-r8v9"
BACKUP_NAME="${1:-openclaw-backup-$(date +%Y%m%d-%H%M%S)}"
BACKUP_DIR="/root/openclaw-backups/${BACKUP_NAME}"
MANIFEST_FILE="${BACKUP_DIR}/backup-manifest.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root"
   exit 1
fi

log_info "Starting OpenClaw backup: ${BACKUP_NAME}"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Create manifest
log_info "Creating backup manifest..."
cat > "${MANIFEST_FILE}" <<EOF
{
  "backup_name": "${BACKUP_NAME}",
  "created_at": "$(date -Iseconds)",
  "hostname": "$(hostname)",
  "openclaw_version": "$(docker exec openclaw-r8v9-openclaw-1 openclaw --version 2>/dev/null || echo 'unknown')",
  "docker_compose_version": "$(docker compose version 2>/dev/null || echo 'unknown')",
  "source_directory": "${OPENCLAW_DIR}"
}
EOF

# Backup Docker configuration
log_info "Backing up Docker configuration..."
mkdir -p "${BACKUP_DIR}/docker"
cp "${OPENCLAW_DIR}/docker-compose.yml" "${BACKUP_DIR}/docker/"
cp "${OPENCLAW_DIR}/.env" "${BACKUP_DIR}/docker/"
cp "${OPENCLAW_DIR}/.build.log" "${BACKUP_DIR}/docker/" 2>/dev/null || true

# Backup OpenClaw configuration
log_info "Backing up OpenClaw configuration..."
mkdir -p "${BACKUP_DIR}/config"
cp -r "${OPENCLAW_DIR}/data/.openclaw" "${BACKUP_DIR}/config/"

# Backup Claude configuration
log_info "Backing up Claude configuration..."
cp "${OPENCLAW_DIR}/data/.claude.json"* "${BACKUP_DIR}/config/" 2>/dev/null || true
cp -r "${OPENCLAW_DIR}/data/.claude" "${BACKUP_DIR}/config/" 2>/dev/null || true

# Backup other configuration files
log_info "Backing up additional configuration files..."
cp "${OPENCLAW_DIR}/data/.gitconfig" "${BACKUP_DIR}/config/" 2>/dev/null || true
cp "${OPENCLAW_DIR}/data/.zshrc" "${BACKUP_DIR}/config/" 2>/dev/null || true

# Backup NPM global packages list
log_info "Backing up NPM global packages..."
docker exec openclaw-r8v9-openclaw-1 npm list -g --depth=0 --json > "${BACKUP_DIR}/config/npm-global-packages.json" 2>/dev/null || true

# Backup projects (if any)
if [ -d "${OPENCLAW_DIR}/data/my-projects" ]; then
    log_info "Backing up projects..."
    mkdir -p "${BACKUP_DIR}/projects"
    cp -r "${OPENCLAW_DIR}/data/my-projects" "${BACKUP_DIR}/projects/"
fi

# Create checksums for all files
log_info "Creating checksums for verification..."
cd "${BACKUP_DIR}"
find . -type f -not -name "checksums.txt" -exec sha256sum {} \; > checksums.txt

# Get current container status
log_info "Capturing container status..."
docker ps -a --filter "name=openclaw" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" > "${BACKUP_DIR}/container-status.txt"

# Export Docker container configuration
log_info "Exporting Docker container configuration..."
docker inspect openclaw-r8v9-openclaw-1 > "${BACKUP_DIR}/docker/container-inspect.json" 2>/dev/null || true

# Get disk usage information
log_info "Recording disk usage..."
du -sh "${OPENCLAW_DIR}/data/.openclaw/workspace" > "${BACKUP_DIR}/disk-usage.txt" 2>/dev/null || true
du -sh "${OPENCLAW_DIR}/data" >> "${BACKUP_DIR}/disk-usage.txt" 2>/dev/null || true

# Create encrypted archive of sensitive data
log_info "Creating encrypted archive..."
ARCHIVE_FILE="/root/openclaw-backups/${BACKUP_NAME}.tar.gz.enc"
tar czf - -C "/root/openclaw-backups" "${BACKUP_NAME}" | \
    openssl enc -aes-256-cbc -salt -pbkdf2 -out "${ARCHIVE_FILE}" -pass pass:"CHANGE_THIS_PASSWORD"

ARCHIVE_SIZE=$(du -h "${ARCHIVE_FILE}" | cut -f1)

log_info "Creating unencrypted archive (for easier transfer if needed)..."
UNENC_ARCHIVE_FILE="/root/openclaw-backups/${BACKUP_NAME}.tar.gz"
tar czf "${UNENC_ARCHIVE_FILE}" -C "/root/openclaw-backups" "${BACKUP_NAME}"
UNENC_SIZE=$(du -h "${UNENC_ARCHIVE_FILE}" | cut -f1)

# Create backup summary
log_info "Creating backup summary..."
cat > "${BACKUP_DIR}/BACKUP-SUMMARY.txt" <<EOF
OpenClaw Backup Summary
======================

Backup Name: ${BACKUP_NAME}
Created: $(date)
Hostname: $(hostname)

Files Backed Up:
- Docker configuration (docker-compose.yml, .env)
- OpenClaw configuration (.openclaw/)
- Claude configuration (.claude/, .claude.json)
- Identity and device authentication
- Workspace files
- Projects
- NPM global packages list

Security Items Included:
- API Keys (Anthropic, OpenAI, Gemini, Perplexity, Brave)
- Discord Bot Token
- Gateway Authentication Tokens
- Device Authentication Keys
- Execution Approvals

Archives Created:
- Encrypted: ${ARCHIVE_FILE} (${ARCHIVE_SIZE})
  Password: CHANGE_THIS_PASSWORD
- Unencrypted: ${UNENC_ARCHIVE_FILE} (${UNENC_SIZE})

Directory Backup: ${BACKUP_DIR}

Verification:
- Checksums: checksums.txt
- Container Status: container-status.txt
- Disk Usage: disk-usage.txt

Next Steps:
1. Transfer the archive to the new server
2. Run the restore script: ./openclaw-restore.sh
3. Run the verification script: ./openclaw-verify.sh

IMPORTANT SECURITY NOTES:
- This backup contains sensitive API keys and tokens
- Store the encrypted archive password securely
- Delete unencrypted archives after transfer
- Use secure transfer methods (scp, rsync over SSH)
EOF

log_info "Backup completed successfully!"
log_info "Backup directory: ${BACKUP_DIR}"
log_info "Encrypted archive: ${ARCHIVE_FILE} (${ARCHIVE_SIZE})"
log_info "Unencrypted archive: ${UNENC_ARCHIVE_FILE} (${UNENC_SIZE})"
log_warn "IMPORTANT: Change the encryption password in the script before production use!"
log_info "Summary: ${BACKUP_DIR}/BACKUP-SUMMARY.txt"

# Display quick stats
echo ""
echo "Backup Statistics:"
echo "=================="
echo "Total files: $(find "${BACKUP_DIR}" -type f | wc -l)"
echo "Total size: $(du -sh "${BACKUP_DIR}" | cut -f1)"
echo ""
echo "To transfer to new server, use:"
echo "  scp ${ARCHIVE_FILE} user@new-server:/root/"
echo ""
echo "Or with rsync:"
echo "  rsync -avz ${ARCHIVE_FILE} user@new-server:/root/"

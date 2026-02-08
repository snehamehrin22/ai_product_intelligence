#!/bin/bash
#
# OpenClaw Direct Transfer Script
# Transfers OpenClaw backup directly to new server
# Usage: ./openclaw-transfer-to-new-server.sh <new-server-ip> [ssh-port]
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

# Get parameters
NEW_SERVER_IP="${1:-}"
SSH_PORT="${2:-22}"

if [ -z "$NEW_SERVER_IP" ]; then
    log_error "Usage: $0 <new-server-ip> [ssh-port]"
    echo "Example: $0 192.168.1.100"
    echo "Example: $0 192.168.1.100 2222"
    exit 1
fi

# Configuration
SOURCE_VPS_IP="187.77.1.7"  # Current VPS IP
BACKUP_DIR="/root/openclaw-backups"
SCRIPTS_DIR="/root"

log_info "OpenClaw Transfer to New Server"
log_info "Source VPS: $SOURCE_VPS_IP"
log_info "Target VPS: $NEW_SERVER_IP"
log_info "SSH Port: $SSH_PORT"
echo ""

# Check if backup exists
log_step "Checking for existing backup..."
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/*.tar.gz.enc 2>/dev/null | head -1 || echo "")

if [ -z "$LATEST_BACKUP" ]; then
    log_warn "No backup found. Creating new backup..."
    /root/openclaw-backup.sh "migration-$(date +%Y%m%d-%H%M%S)"
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/*.tar.gz.enc 2>/dev/null | head -1)
fi

log_info "Using backup: $LATEST_BACKUP"
BACKUP_SIZE=$(du -h "$LATEST_BACKUP" | cut -f1)
log_info "Backup size: $BACKUP_SIZE"
echo ""

# Test SSH connection
log_step "Testing SSH connection to new server..."
if ssh -p "$SSH_PORT" -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@"$NEW_SERVER_IP" "echo 'Connection successful'" 2>/dev/null; then
    log_info "SSH connection successful"
else
    log_error "Cannot connect to new server via SSH"
    log_error "Please ensure:"
    echo "  1. SSH is running on the new server"
    echo "  2. Port $SSH_PORT is open"
    echo "  3. Root login is enabled (or use SSH keys)"
    echo "  4. IP address is correct: $NEW_SERVER_IP"
    exit 1
fi
echo ""

# Transfer backup archive
log_step "Transferring encrypted backup archive..."
log_info "This may take several minutes depending on backup size and network speed..."

if rsync -avz --progress -e "ssh -p $SSH_PORT -o StrictHostKeyChecking=no" \
    "$LATEST_BACKUP" root@"$NEW_SERVER_IP":/root/ ; then
    log_info "Backup archive transferred successfully"
else
    log_error "Failed to transfer backup archive"
    exit 1
fi
echo ""

# Transfer migration scripts
log_step "Transferring migration scripts..."
SCRIPTS=(
    "$SCRIPTS_DIR/openclaw-restore.sh"
    "$SCRIPTS_DIR/openclaw-verify.sh"
    "$SCRIPTS_DIR/openclaw-migration-guide.md"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        log_info "Transferring $(basename $script)..."
        scp -P "$SSH_PORT" -o StrictHostKeyChecking=no "$script" root@"$NEW_SERVER_IP":/root/
    fi
done
echo ""

# Get backup filename
BACKUP_FILENAME=$(basename "$LATEST_BACKUP")

# Create and transfer setup script for new server
log_step "Creating setup script for new server..."
cat > /tmp/setup-new-server.sh <<'SETUP_SCRIPT'
#!/bin/bash
set -euo pipefail

echo "====================================="
echo "  New Server Setup for OpenClaw"
echo "====================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Update system
log_info "Updating system packages..."
apt update && apt upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    log_info "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
else
    log_info "Docker already installed"
fi

# Install Docker Compose plugin
if ! docker compose version &> /dev/null; then
    log_info "Installing Docker Compose..."
    apt install -y docker-compose-plugin
else
    log_info "Docker Compose already installed"
fi

# Install utilities
log_info "Installing utilities..."
apt install -y jq openssl rsync net-tools curl wget git

# Create directory structure
log_info "Creating directory structure..."
mkdir -p /docker
mkdir -p /shared

# Make scripts executable
log_info "Making scripts executable..."
chmod +x /root/openclaw-restore.sh
chmod +x /root/openclaw-verify.sh

echo ""
log_info "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run the restore script:"
echo "   /root/openclaw-restore.sh /root/BACKUP_FILE"
echo ""
echo "2. Start OpenClaw:"
echo "   cd /docker/openclaw-r8v9 && docker compose up -d"
echo ""
echo "3. Verify installation:"
echo "   /root/openclaw-verify.sh"
echo ""
SETUP_SCRIPT

# Replace BACKUP_FILE placeholder
sed -i "s/BACKUP_FILE/$BACKUP_FILENAME/" /tmp/setup-new-server.sh

log_info "Transferring setup script..."
scp -P "$SSH_PORT" -o StrictHostKeyChecking=no /tmp/setup-new-server.sh root@"$NEW_SERVER_IP":/root/
rm /tmp/setup-new-server.sh
echo ""

# Summary and next steps
log_info "Transfer completed successfully!"
echo ""
echo "========================================="
echo "  Transfer Summary"
echo "========================================="
echo "Transferred files:"
echo "  - Backup: $BACKUP_FILENAME ($BACKUP_SIZE)"
echo "  - Restore script: openclaw-restore.sh"
echo "  - Verify script: openclaw-verify.sh"
echo "  - Migration guide: openclaw-migration-guide.md"
echo "  - Setup script: setup-new-server.sh"
echo ""
echo "========================================="
echo "  Next Steps on New Server"
echo "========================================="
echo ""
echo "1. SSH into the new server:"
echo "   ssh -p $SSH_PORT root@$NEW_SERVER_IP"
echo ""
echo "2. Run the setup script (installs Docker, etc.):"
echo "   chmod +x /root/setup-new-server.sh"
echo "   /root/setup-new-server.sh"
echo ""
echo "3. Restore OpenClaw:"
echo "   /root/openclaw-restore.sh /root/$BACKUP_FILENAME"
echo "   # Enter password when prompted: CHANGE_THIS_PASSWORD"
echo ""
echo "4. Start OpenClaw:"
echo "   cd /docker/openclaw-r8v9"
echo "   docker compose up -d"
echo ""
echo "5. Verify installation:"
echo "   /root/openclaw-verify.sh"
echo ""
echo "6. Check logs:"
echo "   docker compose logs -f"
echo ""
log_warn "IMPORTANT: Review and update configuration before starting:"
echo "  - Check ports in .env file"
echo "  - Update any IP-specific settings"
echo "  - Verify API keys are correct"
echo ""
log_info "Migration guide available at: /root/openclaw-migration-guide.md"

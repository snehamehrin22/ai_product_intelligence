#!/bin/bash
#
# Test Migration Readiness
# Verifies everything is ready for migration without making changes
#

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

check_pass() { echo -e "${GREEN}✓${NC} $1"; }
check_fail() { echo -e "${RED}✗${NC} $1"; }
check_info() { echo -e "${YELLOW}ℹ${NC} $1"; }

echo "======================================"
echo "  Migration Readiness Check"
echo "======================================"
echo ""

# Check scripts exist and are executable
echo "1. Checking migration scripts..."
SCRIPTS=("openclaw-backup.sh" "openclaw-restore.sh" "openclaw-verify.sh" "openclaw-transfer-to-new-server.sh")
for script in "${SCRIPTS[@]}"; do
    if [ -x "/root/$script" ]; then
        check_pass "$script is ready"
    else
        check_fail "$script not found or not executable"
    fi
done

echo ""
echo "2. Checking OpenClaw installation..."
if [ -d "/docker/openclaw-r8v9" ]; then
    check_pass "OpenClaw directory exists"
    SIZE=$(du -sh /docker/openclaw-r8v9 2>/dev/null | cut -f1)
    check_info "Installation size: $SIZE"
else
    check_fail "OpenClaw directory not found"
fi

echo ""
echo "3. Checking Docker..."
if docker ps &>/dev/null; then
    check_pass "Docker is accessible"
    if docker ps | grep -q openclaw; then
        check_pass "OpenClaw containers are running"
    else
        check_fail "OpenClaw containers not running"
    fi
else
    check_fail "Cannot access Docker"
fi

echo ""
echo "4. Checking disk space..."
AVAILABLE=$(df -h /root | tail -1 | awk '{print $4}')
check_info "Available space: $AVAILABLE"

echo ""
echo "5. Checking required tools..."
TOOLS=("openssl" "rsync" "jq" "tar")
for tool in "${TOOLS[@]}"; do
    if command -v $tool &>/dev/null; then
        check_pass "$tool is installed"
    else
        check_fail "$tool is not installed"
    fi
done

echo ""
echo "======================================"
echo "  Summary"
echo "======================================"
echo ""
echo "If all checks passed, you're ready to migrate!"
echo ""
echo "Next steps:"
echo "1. Get your new server IP address"
echo "2. Ensure SSH access to new server"
echo "3. Run: /root/openclaw-transfer-to-new-server.sh <NEW_IP>"
echo ""
echo "Or read: /root/QUICK-START-MIGRATION.md"

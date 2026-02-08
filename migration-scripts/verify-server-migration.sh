#!/bin/bash
# Verification script for complete server migration
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

check_pass() { echo -e "${GREEN}✓${NC} $1"; ((PASS++)); }
check_fail() { echo -e "${RED}✗${NC} $1"; ((FAIL++)); }
check_warn() { echo -e "${YELLOW}!${NC} $1"; ((WARN++)); }
check_info() { echo -e "  $1"; }

PASS=0
FAIL=0
WARN=0

echo "========================================"
echo "  Complete Server Migration Verification"
echo "========================================"
echo ""

# 1. Docker & OpenClaw
echo "1. Docker & OpenClaw"
if [ -d "/docker/openclaw-r8v9" ]; then
    check_pass "OpenClaw directory exists"
    if docker ps | grep -q openclaw; then
        check_pass "OpenClaw containers running"
    else
        check_fail "OpenClaw containers not running"
    fi
else
    check_fail "OpenClaw directory not found"
fi

# 2. Shared Folders
echo ""
echo "2. Shared Folders"
for dir in openclaw projects scripts; do
    if [ -d "/shared/$dir" ]; then
        check_pass "/shared/$dir exists"
    else
        check_warn "/shared/$dir not found"
    fi
done

# 3. SSH Keys
echo ""
echo "3. SSH Configuration"
if [ -f "/root/.ssh/id_ed25519" ]; then
    check_pass "SSH private key restored"
else
    check_warn "SSH private key not found"
fi

if [ -f "/root/.ssh/authorized_keys" ]; then
    check_pass "SSH authorized_keys restored"
else
    check_warn "SSH authorized_keys not found"
fi

# 4. Git Configuration
echo ""
echo "4. Git Configuration"
if [ -f "/root/.gitconfig" ]; then
    check_pass "Git config restored"
else
    check_warn "Git config not found"
fi

GIT_REPOS=$(find /shared -name ".git" -type d 2>/dev/null | wc -l)
if [ $GIT_REPOS -gt 0 ]; then
    check_pass "Found $GIT_REPOS Git repositories"
else
    check_warn "No Git repositories found"
fi

# 5. Firewall
echo ""
echo "5. Firewall"
if command -v ufw &>/dev/null; then
    if ufw status | grep -q "Status: active"; then
        check_pass "UFW firewall active"
    else
        check_warn "UFW firewall not active"
    fi
else
    check_warn "UFW not installed"
fi

# 6. Services
echo ""
echo "6. Services"
if docker ps &>/dev/null; then
    check_pass "Docker service running"
else
    check_fail "Docker service not running"
fi

# 7. Configuration Files
echo ""
echo "7. Configuration Files"
if [ -f "/docker/openclaw-r8v9/.env" ]; then
    check_pass ".env file exists"
else
    check_fail ".env file not found"
fi

if [ -f "/docker/openclaw-r8v9/data/.openclaw/openclaw.json" ]; then
    check_pass "openclaw.json exists"
else
    check_fail "openclaw.json not found"
fi

# Summary
echo ""
echo "========================================"
echo "  Summary"
echo "========================================"
echo -e "${GREEN}Passed:${NC}   $PASS"
echo -e "${YELLOW}Warnings:${NC} $WARN"
echo -e "${RED}Failed:${NC}   $FAIL"
echo ""

if [ $FAIL -eq 0 ] && [ $WARN -eq 0 ]; then
    echo -e "${GREEN}✓ Migration successful! All checks passed.${NC}"
    exit 0
elif [ $FAIL -eq 0 ]; then
    echo -e "${YELLOW}! Migration completed with warnings.${NC}"
    exit 0
else
    echo -e "${RED}✗ Migration has issues. Review failed checks.${NC}"
    exit 1
fi

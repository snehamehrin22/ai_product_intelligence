#!/bin/bash
#
# OpenClaw Verification Script
# Verifies OpenClaw installation and configuration
# Usage: ./openclaw-verify.sh
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((CHECKS_PASSED++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((CHECKS_FAILED++))
}

check_warn() {
    echo -e "${YELLOW}!${NC} $1"
    ((CHECKS_WARNING++))
}

check_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Configuration
OPENCLAW_DIR="/docker/openclaw-r8v9"

echo "========================================="
echo "  OpenClaw Installation Verification"
echo "========================================="
echo ""

# Check 1: Directory structure
echo "1. Checking directory structure..."
if [ -d "$OPENCLAW_DIR" ]; then
    check_pass "OpenClaw directory exists: $OPENCLAW_DIR"
else
    check_fail "OpenClaw directory not found: $OPENCLAW_DIR"
fi

if [ -f "$OPENCLAW_DIR/docker-compose.yml" ]; then
    check_pass "docker-compose.yml exists"
else
    check_fail "docker-compose.yml not found"
fi

if [ -f "$OPENCLAW_DIR/.env" ]; then
    check_pass ".env file exists"
else
    check_fail ".env file not found"
fi

# Check 2: OpenClaw configuration
echo ""
echo "2. Checking OpenClaw configuration..."
if [ -f "$OPENCLAW_DIR/data/.openclaw/openclaw.json" ]; then
    check_pass "openclaw.json exists"

    # Validate JSON syntax
    if jq empty "$OPENCLAW_DIR/data/.openclaw/openclaw.json" 2>/dev/null; then
        check_pass "openclaw.json is valid JSON"
    else
        check_fail "openclaw.json has invalid JSON syntax"
    fi

    # Check critical configuration fields
    if jq -e '.agents.defaults.workspace' "$OPENCLAW_DIR/data/.openclaw/openclaw.json" >/dev/null 2>&1; then
        WORKSPACE=$(jq -r '.agents.defaults.workspace' "$OPENCLAW_DIR/data/.openclaw/openclaw.json")
        check_info "Workspace configured: $WORKSPACE"
    fi

    if jq -e '.gateway.port' "$OPENCLAW_DIR/data/.openclaw/openclaw.json" >/dev/null 2>&1; then
        GATEWAY_PORT=$(jq -r '.gateway.port' "$OPENCLAW_DIR/data/.openclaw/openclaw.json")
        check_info "Gateway port: $GATEWAY_PORT"
    fi
else
    check_fail "openclaw.json not found"
fi

# Check 3: API Keys and tokens
echo ""
echo "3. Checking API keys and tokens..."
if [ -f "$OPENCLAW_DIR/.env" ]; then
    if grep -q "ANTHROPIC_API_KEY=" "$OPENCLAW_DIR/.env"; then
        API_KEY=$(grep "ANTHROPIC_API_KEY=" "$OPENCLAW_DIR/.env" | cut -d'=' -f2)
        if [ -n "$API_KEY" ] && [ "$API_KEY" != "your-key-here" ]; then
            check_pass "Anthropic API key configured"
        else
            check_warn "Anthropic API key not set or placeholder value"
        fi
    else
        check_warn "Anthropic API key not found in .env"
    fi

    if grep -q "OPENCLAW_GATEWAY_TOKEN=" "$OPENCLAW_DIR/.env"; then
        check_pass "Gateway token configured"
    else
        check_warn "Gateway token not found in .env"
    fi
fi

# Check 4: Identity and device authentication
echo ""
echo "4. Checking identity and device authentication..."
if [ -f "$OPENCLAW_DIR/data/.openclaw/identity/device-auth.json" ]; then
    check_pass "Device authentication configured"
else
    check_warn "Device authentication not found (may need setup)"
fi

if [ -f "$OPENCLAW_DIR/data/.openclaw/identity/device.json" ]; then
    check_pass "Device identity configured"
else
    check_warn "Device identity not found (may need setup)"
fi

# Check 5: Docker and containers
echo ""
echo "5. Checking Docker setup..."
if command -v docker &> /dev/null; then
    check_pass "Docker is installed"

    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    check_info "Docker version: $DOCKER_VERSION"
else
    check_fail "Docker is not installed"
fi

if command -v docker compose &> /dev/null; then
    check_pass "Docker Compose is available"
else
    check_fail "Docker Compose is not available"
fi

# Check running containers
if docker ps --format '{{.Names}}' | grep -q "openclaw"; then
    check_pass "OpenClaw containers are running"

    echo ""
    check_info "Container status:"
    docker ps --filter "name=openclaw" --format "  - {{.Names}}: {{.Status}}"
else
    check_warn "OpenClaw containers are not running"
    echo "  Start with: cd $OPENCLAW_DIR && docker compose up -d"
fi

# Check 6: Network and ports
echo ""
echo "6. Checking network configuration..."
if [ -f "$OPENCLAW_DIR/.env" ]; then
    PORT=$(grep "^PORT=" "$OPENCLAW_DIR/.env" | cut -d'=' -f2)
    if [ -n "$PORT" ]; then
        check_info "Configured port: $PORT"

        if netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
            check_pass "Port $PORT is in use (likely by OpenClaw)"
        else
            check_warn "Port $PORT is not in use (container may not be running)"
        fi
    fi
fi

# Check 7: Workspace
echo ""
echo "7. Checking workspace..."
if [ -d "$OPENCLAW_DIR/data/.openclaw/workspace" ]; then
    check_pass "Workspace directory exists"

    WORKSPACE_SIZE=$(du -sh "$OPENCLAW_DIR/data/.openclaw/workspace" 2>/dev/null | cut -f1)
    FILE_COUNT=$(find "$OPENCLAW_DIR/data/.openclaw/workspace" -type f 2>/dev/null | wc -l)
    check_info "Workspace size: $WORKSPACE_SIZE ($FILE_COUNT files)"

    if [ $FILE_COUNT -gt 5000 ]; then
        check_warn "Large workspace detected ($FILE_COUNT files) - may impact performance"
    fi
else
    check_warn "Workspace directory not found"
fi

# Check 8: Plugins
echo ""
echo "8. Checking enabled plugins..."
if [ -f "$OPENCLAW_DIR/data/.openclaw/openclaw.json" ]; then
    ENABLED_PLUGINS=$(jq -r '.plugins.entries | to_entries[] | select(.value.enabled == true) | .key' "$OPENCLAW_DIR/data/.openclaw/openclaw.json" 2>/dev/null)
    if [ -n "$ENABLED_PLUGINS" ]; then
        check_info "Enabled plugins:"
        echo "$ENABLED_PLUGINS" | while read plugin; do
            echo "  - $plugin"
        done
    fi
fi

# Check 9: Security settings
echo ""
echo "9. Checking security settings..."
if [ -f "$OPENCLAW_DIR/data/.openclaw/openclaw.json" ]; then
    # Check gateway auth
    AUTH_MODE=$(jq -r '.gateway.auth.mode' "$OPENCLAW_DIR/data/.openclaw/openclaw.json" 2>/dev/null)
    if [ "$AUTH_MODE" = "token" ]; then
        check_pass "Gateway authentication enabled (token mode)"
    else
        check_warn "Gateway authentication mode: $AUTH_MODE"
    fi

    # Check insecure auth
    INSECURE_AUTH=$(jq -r '.gateway.controlUi.allowInsecureAuth' "$OPENCLAW_DIR/data/.openclaw/openclaw.json" 2>/dev/null)
    if [ "$INSECURE_AUTH" = "true" ]; then
        check_warn "Insecure authentication is allowed - consider disabling in production"
    else
        check_pass "Insecure authentication is disabled"
    fi
fi

# Check 10: File permissions
echo ""
echo "10. Checking file permissions..."
DATA_OWNER=$(stat -c '%U' "$OPENCLAW_DIR/data" 2>/dev/null || stat -f '%Su' "$OPENCLAW_DIR/data" 2>/dev/null)
if [ "$DATA_OWNER" = "ubuntu" ] || [ "$DATA_OWNER" = "1000" ]; then
    check_pass "Data directory has correct ownership: $DATA_OWNER"
else
    check_warn "Data directory ownership: $DATA_OWNER (expected: ubuntu or 1000)"
fi

# Summary
echo ""
echo "========================================="
echo "  Verification Summary"
echo "========================================="
echo -e "${GREEN}Passed:${NC}  $CHECKS_PASSED"
echo -e "${YELLOW}Warnings:${NC} $CHECKS_WARNING"
echo -e "${RED}Failed:${NC}  $CHECKS_FAILED"
echo ""

if [ $CHECKS_FAILED -eq 0 ] && [ $CHECKS_WARNING -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! OpenClaw is properly configured.${NC}"
    exit 0
elif [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${YELLOW}! Some warnings found. Review and address them if needed.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review and fix the issues above.${NC}"
    exit 1
fi

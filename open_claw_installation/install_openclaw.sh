#!/bin/bash

#############################################################################
# OpenClaw Installation Script for Hostinger VPS (Ubuntu 22.04/24.04)
# This script automates the manual installation process (Path B)
#
# Usage:
#   chmod +x install_openclaw.sh
#   ./install_openclaw.sh
#
# Prerequisites:
#   - Ubuntu 22.04 or 24.04 LTS
#   - Root or sudo privileges
#   - Internet connection
#############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
OPENCLAW_DIR="/opt/openclaw"
INSTALL_USER="${SUDO_USER:-$USER}"

#############################################################################
# Helper Functions
#############################################################################

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root or with sudo"
        exit 1
    fi
}

check_os() {
    if [[ ! -f /etc/os-release ]]; then
        print_error "Cannot detect OS version"
        exit 1
    fi

    . /etc/os-release

    if [[ "$ID" != "ubuntu" ]]; then
        print_warning "This script is designed for Ubuntu. Detected: $ID"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    if [[ "$VERSION_ID" != "22.04" && "$VERSION_ID" != "24.04" ]]; then
        print_warning "Recommended Ubuntu version: 22.04 or 24.04. Detected: $VERSION_ID"
    fi
}

#############################################################################
# Installation Steps
#############################################################################

step_1_update_system() {
    print_header "Step 1: Updating System Packages"

    apt update -qq
    apt upgrade -y -qq

    print_success "System packages updated"
}

step_2_install_prerequisites() {
    print_header "Step 2: Installing Prerequisites"

    print_info "Installing required packages..."
    apt install -y -qq \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        git \
        ufw \
        software-properties-common

    print_success "Prerequisites installed"
}

step_3_install_docker() {
    print_header "Step 3: Installing Docker & Docker Compose"

    # Check if Docker is already installed
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
        print_info "Docker already installed: $DOCKER_VERSION"
        read -p "Reinstall Docker? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    fi

    # Add Docker's official GPG key
    print_info "Adding Docker GPG key..."
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
        gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Set up Docker repository
    print_info "Adding Docker repository..."
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine
    print_info "Installing Docker Engine..."
    apt update -qq
    apt install -y -qq \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin

    # Verify installation
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
    COMPOSE_VERSION=$(docker compose version | awk '{print $4}')

    print_success "Docker installed: $DOCKER_VERSION"
    print_success "Docker Compose installed: $COMPOSE_VERSION"

    # Add user to docker group
    if [[ -n "$INSTALL_USER" && "$INSTALL_USER" != "root" ]]; then
        usermod -aG docker "$INSTALL_USER"
        print_success "User $INSTALL_USER added to docker group"
        print_warning "User needs to log out and back in for group changes to take effect"
    fi
}

step_4_clone_repository() {
    print_header "Step 4: Cloning OpenClaw Repository"

    # Remove existing directory if present
    if [[ -d "$OPENCLAW_DIR" ]]; then
        print_warning "Directory $OPENCLAW_DIR already exists"
        read -p "Remove and re-clone? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$OPENCLAW_DIR"
        else
            print_info "Using existing repository"
            return
        fi
    fi

    # Clone repository
    print_info "Cloning OpenClaw repository..."
    git clone https://github.com/openclaw/openclaw.git "$OPENCLAW_DIR"

    # Set ownership
    if [[ -n "$INSTALL_USER" && "$INSTALL_USER" != "root" ]]; then
        chown -R "$INSTALL_USER:$INSTALL_USER" "$OPENCLAW_DIR"
    fi

    print_success "Repository cloned to $OPENCLAW_DIR"
}

step_5_run_docker_setup() {
    print_header "Step 5: Running OpenClaw Docker Setup"

    cd "$OPENCLAW_DIR"

    # Make setup script executable
    chmod +x docker-setup.sh

    print_info "Starting OpenClaw setup wizard..."
    print_warning "You will be prompted to:"
    print_warning "  1. Choose your AI provider (Anthropic, OpenAI, etc.)"
    print_warning "  2. Enter your API key"
    print_warning "  3. Select AI model"
    print_warning "  4. Configure security settings"
    echo ""
    print_warning "IMPORTANT: Save the gateway token shown at the end!"
    echo ""

    read -p "Press Enter to continue..."

    # Run setup as the installation user if not root
    if [[ -n "$INSTALL_USER" && "$INSTALL_USER" != "root" ]]; then
        sudo -u "$INSTALL_USER" ./docker-setup.sh
    else
        ./docker-setup.sh
    fi

    print_success "OpenClaw setup completed"
}

step_6_configure_firewall() {
    print_header "Step 6: Configuring Firewall"

    print_info "Configuring UFW firewall..."

    # Enable UFW if not already enabled
    if ! ufw status | grep -q "Status: active"; then
        print_info "Enabling UFW..."
        ufw --force enable
    fi

    # Default policies
    ufw default deny incoming
    ufw default allow outgoing

    # Allow SSH
    ufw allow ssh
    print_success "SSH access allowed"

    # Allow OpenClaw port
    ufw allow 18789/tcp
    print_success "OpenClaw port 18789 allowed"

    # Allow HTTP/HTTPS (if setting up reverse proxy)
    read -p "Allow HTTP/HTTPS ports (for reverse proxy)? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ufw allow 80/tcp
        ufw allow 443/tcp
        print_success "HTTP/HTTPS ports allowed"
    fi

    # Reload firewall
    ufw reload

    print_success "Firewall configured"
}

step_7_verify_installation() {
    print_header "Step 7: Verifying Installation"

    cd "$OPENCLAW_DIR"

    print_info "Checking Docker containers..."
    sleep 3  # Wait for containers to start

    if docker compose ps | grep -q "Up"; then
        print_success "OpenClaw containers are running"
    else
        print_error "OpenClaw containers are not running"
        print_info "Checking logs..."
        docker compose logs --tail=20
        return 1
    fi

    # Check if port 18789 is listening
    if netstat -tlnp 2>/dev/null | grep -q ":18789"; then
        print_success "OpenClaw gateway listening on port 18789"
    else
        print_warning "Port 18789 not listening (may need a moment to start)"
    fi

    # Run health check
    print_info "Running health check..."
    if docker compose run --rm openclaw-cli doctor 2>/dev/null; then
        print_success "Health check passed"
    else
        print_warning "Health check had issues (check above output)"
    fi
}

display_completion_info() {
    print_header "Installation Complete!"

    # Get server IP
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_SERVER_IP")

    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}OpenClaw has been installed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}\n"

    echo -e "${BLUE}Access your OpenClaw dashboard:${NC}"
    echo -e "  ${YELLOW}http://$SERVER_IP:18789${NC}\n"

    echo -e "${BLUE}Next Steps:${NC}"
    echo -e "  1. Open the URL above in your browser"
    echo -e "  2. Enter your gateway token (shown during setup)"
    echo -e "  3. Complete the onboarding wizard"
    echo -e "  4. Connect your messaging platforms\n"

    echo -e "${BLUE}Useful Commands:${NC}"
    echo -e "  View logs:          ${YELLOW}cd $OPENCLAW_DIR && docker compose logs -f${NC}"
    echo -e "  Restart OpenClaw:   ${YELLOW}cd $OPENCLAW_DIR && docker compose restart${NC}"
    echo -e "  Stop OpenClaw:      ${YELLOW}cd $OPENCLAW_DIR && docker compose down${NC}"
    echo -e "  Start OpenClaw:     ${YELLOW}cd $OPENCLAW_DIR && docker compose up -d${NC}"
    echo -e "  Health check:       ${YELLOW}cd $OPENCLAW_DIR && docker compose run --rm openclaw-cli doctor${NC}\n"

    echo -e "${BLUE}Documentation:${NC}"
    echo -e "  Installation Guide: ${YELLOW}$OPENCLAW_DIR/../INSTALLATION_GUIDE.md${NC}"
    echo -e "  Official Docs:      ${YELLOW}https://docs.openclaw.ai/${NC}\n"

    if [[ -n "$INSTALL_USER" && "$INSTALL_USER" != "root" ]]; then
        echo -e "${YELLOW}NOTE: User $INSTALL_USER must log out and back in for Docker group changes to take effect.${NC}\n"
    fi

    print_success "Happy automating with OpenClaw!"
}

display_error_info() {
    print_header "Installation Failed"

    echo -e "${RED}The installation encountered an error.${NC}\n"

    echo -e "${BLUE}Troubleshooting Steps:${NC}"
    echo -e "  1. Check the error messages above"
    echo -e "  2. Review logs: ${YELLOW}cd $OPENCLAW_DIR && docker compose logs${NC}"
    echo -e "  3. Consult the installation guide"
    echo -e "  4. Check GitHub issues: ${YELLOW}https://github.com/openclaw/openclaw/issues${NC}\n"

    echo -e "${BLUE}Common Issues:${NC}"
    echo -e "  - Insufficient disk space: Run ${YELLOW}df -h${NC}"
    echo -e "  - Docker not running: Run ${YELLOW}systemctl status docker${NC}"
    echo -e "  - Port already in use: Run ${YELLOW}netstat -tlnp | grep 18789${NC}"
    echo -e "  - Network issues: Check internet connectivity\n"

    exit 1
}

#############################################################################
# Main Installation Flow
#############################################################################

main() {
    clear

    cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ___                   ____ _                            ║
║  / _ \ _ __   ___ _ __ / ___| | __ ___      __            ║
║ | | | | '_ \ / _ \ '_ \| |   | |/ _` \ \ /\ / /           ║
║ | |_| | |_) |  __/ | | | |___| | (_| |\ V  V /            ║
║  \___/| .__/ \___|_| |_|\____|_|\__,_| \_/\_/             ║
║       |_|                                                 ║
║                                                           ║
║         Installation Script for Hostinger VPS            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF

    echo -e "\n${BLUE}This script will install OpenClaw on your Ubuntu VPS${NC}"
    echo -e "${BLUE}Installation directory: $OPENCLAW_DIR${NC}\n"

    # Pre-flight checks
    check_root
    check_os

    print_info "Starting installation in 3 seconds..."
    sleep 3

    # Run installation steps
    if step_1_update_system && \
       step_2_install_prerequisites && \
       step_3_install_docker && \
       step_4_clone_repository && \
       step_5_run_docker_setup && \
       step_6_configure_firewall && \
       step_7_verify_installation; then
        display_completion_info
    else
        display_error_info
    fi
}

#############################################################################
# Script Entry Point
#############################################################################

# Trap errors
trap 'print_error "An error occurred. Installation aborted."; exit 1' ERR

# Run main installation
main "$@"

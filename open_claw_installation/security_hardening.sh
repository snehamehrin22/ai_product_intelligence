#!/bin/bash

#############################################################################
# OpenClaw Security Hardening Script
# Automates essential security configurations for Hostinger VPS
#
# Usage:
#   chmod +x security_hardening.sh
#   sudo ./security_hardening.sh
#
# What this script does:
#   1. Configures UFW firewall
#   2. Installs and configures Fail2Ban
#   3. Sets up automatic security updates
#   4. Configures OpenClaw to bind localhost only
#   5. Sets up backup automation
#   6. Hardens SSH (optional)
#############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
OPENCLAW_DIR="/opt/openclaw"
BACKUP_DIR="/root/openclaw-backups"

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

#############################################################################
# Security Hardening Steps
#############################################################################

step_1_configure_firewall() {
    print_header "Step 1: Configuring UFW Firewall"

    # Check if UFW is installed
    if ! command -v ufw &> /dev/null; then
        print_info "Installing UFW..."
        apt update -qq
        apt install -y ufw
    fi

    print_warning "IMPORTANT: Configuring firewall rules..."
    print_warning "If you're using a custom SSH port, you'll need to update the rules."
    echo ""

    # Default policies
    print_info "Setting default policies..."
    ufw --force default deny incoming
    ufw --force default allow outgoing

    # Ask about SSH port
    read -p "What SSH port are you using? (default: 22): " SSH_PORT
    SSH_PORT=${SSH_PORT:-22}

    # Allow SSH
    print_info "Allowing SSH on port $SSH_PORT..."
    ufw allow $SSH_PORT/tcp

    # Allow HTTP/HTTPS for reverse proxy
    read -p "Will you set up SSL/HTTPS with reverse proxy? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_info "Allowing HTTP/HTTPS..."
        ufw allow 80/tcp
        ufw allow 443/tcp
        SETUP_REVERSE_PROXY=true
    fi

    # Do NOT allow port 18789 directly
    print_info "OpenClaw port 18789 will NOT be exposed directly (security best practice)"

    # Enable firewall
    print_info "Enabling firewall..."
    ufw --force enable

    # Show status
    print_success "Firewall configured successfully"
    ufw status verbose

    echo ""
    print_warning "IMPORTANT: Test SSH connection in a NEW terminal before closing this session!"
    echo ""
    read -p "Press Enter to continue once you've confirmed SSH access..."
}

step_2_install_fail2ban() {
    print_header "Step 2: Installing and Configuring Fail2Ban"

    # Install Fail2Ban
    if ! command -v fail2ban-client &> /dev/null; then
        print_info "Installing Fail2Ban..."
        apt install -y fail2ban
    else
        print_info "Fail2Ban already installed"
    fi

    # Create custom configuration
    print_info "Creating Fail2Ban configuration..."
    cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ${SSH_PORT:-22}
logpath = /var/log/auth.log
maxretry = 5

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
maxretry = 10
EOF

    # Start and enable Fail2Ban
    systemctl restart fail2ban
    systemctl enable fail2ban

    print_success "Fail2Ban configured and started"

    # Show status
    sleep 2
    fail2ban-client status
}

step_3_automatic_updates() {
    print_header "Step 3: Configuring Automatic Security Updates"

    # Install unattended-upgrades
    if ! dpkg -l | grep -q unattended-upgrades; then
        print_info "Installing unattended-upgrades..."
        apt install -y unattended-upgrades
    fi

    # Configure
    print_info "Configuring automatic updates..."
    cat > /etc/apt/apt.conf.d/20auto-upgrades <<EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF

    # Configure unattended-upgrades
    cat > /etc/apt/apt.conf.d/50unattended-upgrades <<EOF
Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}-security";
    "\${distro_id}ESMApps:\${distro_codename}-apps-security";
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

    print_success "Automatic security updates enabled"

    # Test
    print_info "Testing configuration..."
    unattended-upgrades --dry-run
}

step_4_secure_openclaw() {
    print_header "Step 4: Securing OpenClaw Configuration"

    if [[ ! -d "$OPENCLAW_DIR" ]]; then
        print_warning "OpenClaw directory not found at $OPENCLAW_DIR"
        read -p "Enter OpenClaw installation directory: " OPENCLAW_DIR
    fi

    cd "$OPENCLAW_DIR"

    # Backup original docker-compose.yml
    if [[ -f docker-compose.yml ]]; then
        print_info "Backing up docker-compose.yml..."
        cp docker-compose.yml docker-compose.yml.backup

        # Check if already configured for localhost
        if grep -q "127.0.0.1:18789" docker-compose.yml; then
            print_info "OpenClaw already configured to bind localhost only"
        else
            print_info "Configuring OpenClaw to bind localhost only..."

            # This is a simple sed replacement - may need manual adjustment
            print_warning "You may need to manually verify docker-compose.yml"
            print_info "Change: '18789:18789' to '127.0.0.1:18789:18789'"

            read -p "Modify docker-compose.yml now? (Y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                nano docker-compose.yml
            fi
        fi
    fi

    # Regenerate gateway token
    read -p "Regenerate gateway token for security? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Regenerating gateway token..."
        docker compose run --rm openclaw-cli auth regenerate-token || print_warning "Could not regenerate token - do manually"
    fi

    # Enable sandbox mode
    print_info "Checking sandbox configuration..."
    if grep -q "OPENCLAW_SANDBOX_MODE" docker-compose.yml; then
        print_info "Sandbox mode already configured"
    else
        print_info "Consider adding OPENCLAW_SANDBOX_MODE=non-main to docker-compose.yml"
    fi

    print_success "OpenClaw security configuration reviewed"
}

step_5_setup_backups() {
    print_header "Step 5: Setting Up Automated Backups"

    # Create backup directory
    mkdir -p "$BACKUP_DIR"

    # Create backup script
    print_info "Creating backup script..."
    cat > /usr/local/bin/backup-openclaw.sh <<'EOF'
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

# Backup Nginx config (if exists)
if [[ -f /etc/nginx/sites-available/openclaw ]]; then
    tar -czf $BACKUP_DIR/nginx_config_$DATE.tar.gz \
        /etc/nginx/sites-available/openclaw \
        /etc/letsencrypt 2>/dev/null
fi

# Remove old backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Log
echo "Backup completed: $(date)" >> $BACKUP_DIR/backup.log

# Keep only last 100 log entries
tail -100 $BACKUP_DIR/backup.log > $BACKUP_DIR/backup.log.tmp
mv $BACKUP_DIR/backup.log.tmp $BACKUP_DIR/backup.log
EOF

    chmod +x /usr/local/bin/backup-openclaw.sh

    # Test backup
    print_info "Testing backup..."
    /usr/local/bin/backup-openclaw.sh

    if [[ -f "$BACKUP_DIR/backup.log" ]]; then
        print_success "Backup test successful"
        ls -lh "$BACKUP_DIR/" | tail -3
    fi

    # Setup cron job
    print_info "Setting up daily backups at 2 AM..."

    # Check if cron entry already exists
    if crontab -l 2>/dev/null | grep -q "backup-openclaw.sh"; then
        print_info "Backup cron job already exists"
    else
        (crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-openclaw.sh") | crontab -
        print_success "Daily backup scheduled"
    fi
}

step_6_ssh_hardening() {
    print_header "Step 6: SSH Hardening (Optional)"

    print_warning "SSH hardening can lock you out if not done carefully!"
    read -p "Do you want to harden SSH configuration? (y/N): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Skipping SSH hardening"
        return
    fi

    # Backup SSH config
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

    print_info "SSH hardening options:"
    echo "1. Disable root login (recommended after creating sudo user)"
    echo "2. Disable password authentication (require SSH keys)"
    echo "3. Change SSH port"
    echo "4. All of the above"
    echo "5. Skip"

    read -p "Choose option (1-5): " -n 1 -r SSH_OPTION
    echo

    case $SSH_OPTION in
        1)
            print_warning "Ensure you have a sudo user created first!"
            read -p "Disable root login? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
                print_success "Root login disabled"
            fi
            ;;
        2)
            print_warning "Ensure you have SSH keys set up first!"
            read -p "Disable password authentication? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                sed -i 's/^PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
                print_success "Password authentication disabled"
            fi
            ;;
        3)
            read -p "Enter new SSH port (e.g., 2222): " NEW_SSH_PORT
            if [[ -n "$NEW_SSH_PORT" ]]; then
                sed -i "s/^Port.*/Port $NEW_SSH_PORT/" /etc/ssh/sshd_config
                ufw allow $NEW_SSH_PORT/tcp
                print_success "SSH port changed to $NEW_SSH_PORT"
                print_warning "Update your firewall and test before closing this session!"
            fi
            ;;
        4)
            print_error "Manual configuration recommended for 'all of the above'"
            ;;
        *)
            print_info "Skipping SSH hardening"
            return
            ;;
    esac

    # Ask to restart SSH
    read -p "Restart SSH daemon now? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        systemctl restart sshd
        print_success "SSH daemon restarted"
        print_warning "Test SSH connection in a NEW terminal before closing this one!"
    fi
}

step_7_security_report() {
    print_header "Step 7: Security Configuration Report"

    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Security Hardening Complete!${NC}"
    echo -e "${GREEN}========================================${NC}\n"

    echo -e "${BLUE}Security Status:${NC}"

    # Firewall
    if ufw status | grep -q "Status: active"; then
        print_success "Firewall: Active"
    else
        print_warning "Firewall: Inactive"
    fi

    # Fail2Ban
    if systemctl is-active --quiet fail2ban; then
        print_success "Fail2Ban: Running"
    else
        print_warning "Fail2Ban: Not running"
    fi

    # Automatic updates
    if [[ -f /etc/apt/apt.conf.d/20auto-upgrades ]]; then
        print_success "Automatic Updates: Enabled"
    else
        print_warning "Automatic Updates: Not configured"
    fi

    # Backups
    if [[ -f /usr/local/bin/backup-openclaw.sh ]]; then
        print_success "Automated Backups: Configured"
        echo "  Latest backup: $(ls -t $BACKUP_DIR/*.tar.gz 2>/dev/null | head -1)"
    else
        print_warning "Automated Backups: Not configured"
    fi

    # OpenClaw status
    if docker compose -f "$OPENCLAW_DIR/docker-compose.yml" ps | grep -q "Up"; then
        print_success "OpenClaw: Running"
    else
        print_warning "OpenClaw: Not running"
    fi

    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Set up SSL/HTTPS with reverse proxy (see SECURITY_GUIDE.md)"
    echo "2. Test all services are accessible"
    echo "3. Review and adjust firewall rules as needed"
    echo "4. Schedule regular security audits (monthly)"
    echo "5. Monitor logs for suspicious activity"

    echo ""
    echo -e "${BLUE}Important Files:${NC}"
    echo "  Security Guide: SECURITY_GUIDE.md"
    echo "  Backup Script: /usr/local/bin/backup-openclaw.sh"
    echo "  Backups Location: $BACKUP_DIR"
    echo "  Firewall Config: ufw status verbose"
    echo "  Fail2Ban Config: /etc/fail2ban/jail.local"

    echo ""
    echo -e "${BLUE}Security Commands:${NC}"
    echo "  Check firewall: ${YELLOW}sudo ufw status verbose${NC}"
    echo "  Check Fail2Ban: ${YELLOW}sudo fail2ban-client status${NC}"
    echo "  Check backups: ${YELLOW}ls -lh $BACKUP_DIR${NC}"
    echo "  Manual backup: ${YELLOW}sudo /usr/local/bin/backup-openclaw.sh${NC}"
    echo "  View logs: ${YELLOW}cd $OPENCLAW_DIR && docker compose logs${NC}"

    echo ""
    print_success "Security hardening completed successfully!"
}

#############################################################################
# Main Flow
#############################################################################

main() {
    clear

    cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           OpenClaw Security Hardening Script             ║
║                                                           ║
║  This script will configure essential security measures  ║
║  for your OpenClaw installation on Hostinger VPS         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF

    echo -e "\n${BLUE}Security measures to be configured:${NC}"
    echo "  1. UFW Firewall"
    echo "  2. Fail2Ban (brute force protection)"
    echo "  3. Automatic security updates"
    echo "  4. OpenClaw localhost binding"
    echo "  5. Automated backups"
    echo "  6. SSH hardening (optional)"
    echo ""

    print_warning "IMPORTANT: This script will modify system configuration."
    print_warning "Ensure you have console access via Hostinger VPS panel in case of issues."
    echo ""

    read -p "Continue with security hardening? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Security hardening cancelled"
        exit 0
    fi

    # Pre-flight check
    check_root

    # Run hardening steps
    step_1_configure_firewall
    step_2_install_fail2ban
    step_3_automatic_updates
    step_4_secure_openclaw
    step_5_setup_backups
    step_6_ssh_hardening
    step_7_security_report
}

# Trap errors
trap 'print_error "An error occurred. Check output above."; exit 1' ERR

# Run main
main "$@"

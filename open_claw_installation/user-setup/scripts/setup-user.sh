#!/bin/bash

#############################################################################
# User Account Setup Script for VPS
# Sets up regular user with sudo, Git, and Claude Code
#
# Usage (as root):
#   chmod +x setup_user_account.sh
#   ./setup_user_account.sh
#
# What this script does:
#   1. Creates new user with sudo access
#   2. Sets up SSH access for user
#   3. Installs and configures Git
#   4. Configures GitHub SSH access
#   5. Provides instructions for Claude Code setup
#############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

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
    echo -e "${CYAN}ℹ $1${NC}"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

#############################################################################
# Setup Steps
#############################################################################

step_1_create_user() {
    print_header "Step 1: Creating User Account"

    read -p "Enter username for new account: " USERNAME

    if id "$USERNAME" &>/dev/null; then
        print_warning "User $USERNAME already exists"
        read -p "Continue with existing user? (Y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            exit 1
        fi
    else
        print_info "Creating user: $USERNAME"
        adduser "$USERNAME"

        if [ $? -eq 0 ]; then
            print_success "User $USERNAME created"
        else
            print_error "Failed to create user"
            exit 1
        fi
    fi

    # Add to sudo group
    print_info "Adding $USERNAME to sudo group..."
    usermod -aG sudo "$USERNAME"
    print_success "User $USERNAME has sudo access"
}

step_2_setup_ssh() {
    print_header "Step 2: Setting Up SSH Access"

    USER_HOME=$(eval echo ~$USERNAME)

    print_info "SSH setup options:"
    echo "1. Copy root's SSH keys (quick)"
    echo "2. I'll add my own SSH key manually (advanced)"
    echo "3. Skip SSH setup"

    read -p "Choose option (1-3): " -n 1 -r SSH_OPTION
    echo

    case $SSH_OPTION in
        1)
            print_info "Copying SSH keys from root to $USERNAME..."

            # Create .ssh directory
            mkdir -p "$USER_HOME/.ssh"

            # Copy authorized_keys if exists
            if [ -f ~/.ssh/authorized_keys ]; then
                cp ~/.ssh/authorized_keys "$USER_HOME/.ssh/"
                print_success "SSH keys copied"
            else
                print_warning "No authorized_keys found in root account"
                print_info "You'll need to add SSH keys manually"
            fi

            # Set permissions
            chown -R "$USERNAME:$USERNAME" "$USER_HOME/.ssh"
            chmod 700 "$USER_HOME/.ssh"
            chmod 600 "$USER_HOME/.ssh/authorized_keys" 2>/dev/null || true

            print_success "SSH directory configured"
            ;;
        2)
            print_info "Creating .ssh directory for $USERNAME..."
            mkdir -p "$USER_HOME/.ssh"
            touch "$USER_HOME/.ssh/authorized_keys"
            chown -R "$USERNAME:$USERNAME" "$USER_HOME/.ssh"
            chmod 700 "$USER_HOME/.ssh"
            chmod 600 "$USER_HOME/.ssh/authorized_keys"

            print_info "SSH directory created"
            print_warning "Add your public key to: $USER_HOME/.ssh/authorized_keys"
            print_info "From your local machine, run:"
            echo "  ssh-copy-id $USERNAME@$(hostname -I | awk '{print $1}')"
            ;;
        3)
            print_warning "Skipping SSH setup"
            print_info "User will need to use password for SSH login"
            ;;
    esac
}

step_3_install_git() {
    print_header "Step 3: Installing Git"

    # Check if git is installed
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        print_info "Git already installed: $GIT_VERSION"
    else
        print_info "Installing Git..."
        apt update -qq
        apt install -y git

        if command -v git &> /dev/null; then
            print_success "Git installed: $(git --version)"
        else
            print_error "Git installation failed"
            return
        fi
    fi
}

step_4_git_config() {
    print_header "Step 4: Configuring Git for User"

    read -p "Enter Git username (e.g., 'John Doe'): " GIT_NAME
    read -p "Enter Git email (e.g., 'john@example.com'): " GIT_EMAIL

    # Configure git as the user
    sudo -u "$USERNAME" git config --global user.name "$GIT_NAME"
    sudo -u "$USERNAME" git config --global user.email "$GIT_EMAIL"

    print_success "Git configured for $USERNAME"
    print_info "Name: $GIT_NAME"
    print_info "Email: $GIT_EMAIL"
}

step_5_github_ssh() {
    print_header "Step 5: GitHub SSH Setup"

    print_info "Setting up GitHub SSH access for $USERNAME"

    USER_HOME=$(eval echo ~$USERNAME)

    # Generate SSH key for GitHub
    print_info "Generating SSH key for GitHub..."

    read -p "Enter email for GitHub SSH key: " GITHUB_EMAIL

    sudo -u "$USERNAME" ssh-keygen -t ed25519 -C "$GITHUB_EMAIL" -f "$USER_HOME/.ssh/id_ed25519_github" -N ""

    if [ -f "$USER_HOME/.ssh/id_ed25519_github.pub" ]; then
        print_success "SSH key generated"

        # Create SSH config
        print_info "Creating SSH config..."

        cat > "$USER_HOME/.ssh/config" <<EOF
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_github
  IdentitiesOnly yes
EOF

        chown "$USERNAME:$USERNAME" "$USER_HOME/.ssh/config"
        chmod 600 "$USER_HOME/.ssh/config"

        print_success "SSH config created"

        # Display public key
        echo ""
        print_warning "=========================================="
        print_warning "IMPORTANT: Add this key to GitHub"
        print_warning "=========================================="
        echo ""
        cat "$USER_HOME/.ssh/id_ed25519_github.pub"
        echo ""
        print_info "1. Copy the key above"
        print_info "2. Go to: https://github.com/settings/keys"
        print_info "3. Click 'New SSH key'"
        print_info "4. Paste the key and save"
        echo ""

        read -p "Press Enter once you've added the key to GitHub..."

        # Test connection
        print_info "Testing GitHub connection..."
        if sudo -u "$USERNAME" ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
            print_success "GitHub connection successful!"
        else
            print_warning "GitHub connection test failed (this is normal if you haven't added the key yet)"
        fi
    else
        print_error "SSH key generation failed"
    fi
}

step_6_clone_repo() {
    print_header "Step 6: Cloning Repository"

    read -p "Do you want to clone the ai_product_intelligence repository now? (Y/n): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Skipping repository clone"
        return
    fi

    USER_HOME=$(eval echo ~$USERNAME)

    # Create projects directory
    print_info "Creating projects directory..."
    sudo -u "$USERNAME" mkdir -p "$USER_HOME/projects"

    # Clone repository
    print_info "Cloning repository..."

    cd "$USER_HOME/projects"

    if sudo -u "$USERNAME" git clone git@github.com:snehamehrin22/ai_product_intelligence.git; then
        print_success "Repository cloned successfully"
        print_info "Location: $USER_HOME/projects/ai_product_intelligence"
    else
        print_error "Failed to clone repository"
        print_warning "Make sure you've added the SSH key to GitHub"
        print_info "You can clone manually later:"
        echo "  cd ~/projects"
        echo "  git clone git@github.com:snehamehrin22/ai_product_intelligence.git"
    fi
}

step_7_next_steps() {
    print_header "Setup Complete! Next Steps"

    USER_HOME=$(eval echo ~$USERNAME)
    SERVER_IP=$(hostname -I | awk '{print $1}')

    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}User Account Setup Complete!${NC}"
    echo -e "${GREEN}========================================${NC}\n"

    echo -e "${BLUE}Account Details:${NC}"
    echo "  Username: $USERNAME"
    echo "  Home: $USER_HOME"
    echo "  Sudo: Enabled"
    echo "  Git: Configured"
    echo "  GitHub SSH: Configured"
    echo ""

    echo -e "${BLUE}To SSH as $USERNAME:${NC}"
    echo "  ${YELLOW}ssh $USERNAME@$SERVER_IP${NC}"
    echo ""

    echo -e "${BLUE}Next Steps (as $USERNAME):${NC}"
    echo ""
    echo "1. SSH to server as $USERNAME"
    echo ""
    echo "2. Install Claude Code:"
    echo "   ${YELLOW}curl -fsSL https://claude.ai/install.sh | bash${NC}"
    echo "   ${YELLOW}source ~/.bashrc${NC}"
    echo "   ${YELLOW}claude --version${NC}"
    echo ""
    echo "3. Authenticate Claude Code:"
    echo "   ${YELLOW}claude /login${NC}"
    echo "   (Use SSH port forwarding - see USER_SETUP_GUIDE.md)"
    echo ""
    echo "4. Install tmux:"
    echo "   ${YELLOW}sudo apt install -y tmux${NC}"
    echo ""
    echo "5. Navigate to project:"
    echo "   ${YELLOW}cd ~/projects/ai_product_intelligence/open_claw_installation${NC}"
    echo ""
    echo "6. Start working!"
    echo "   ${YELLOW}tmux new -s claude${NC}"
    echo "   ${YELLOW}claude${NC}"
    echo ""

    echo -e "${BLUE}Documentation:${NC}"
    echo "  Full guide: $USER_HOME/projects/ai_product_intelligence/open_claw_installation/USER_SETUP_GUIDE.md"
    echo "  Claude Code: CLAUDE_CODE_INSTALLATION.md"
    echo ""

    echo -e "${BLUE}Test Your Setup:${NC}"
    echo "  ${YELLOW}su - $USERNAME${NC}  (switch to user)"
    echo "  ${YELLOW}git --version${NC}   (verify git)"
    echo "  ${YELLOW}sudo whoami${NC}     (test sudo - should show 'root')"
    echo "  ${YELLOW}exit${NC}            (return to root)"
    echo ""

    print_success "Setup complete! Happy coding! 🚀"
}

#############################################################################
# Main Flow
#############################################################################

main() {
    clear

    cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║             VPS User Account Setup Script                ║
║                                                           ║
║  Sets up regular user with:                              ║
║  • Sudo access                                           ║
║  • SSH configuration                                     ║
║  • Git and GitHub access                                 ║
║  • Ready for Claude Code installation                    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF

    echo ""
    print_warning "This script will create a new user account and configure it."
    echo ""

    read -p "Continue? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Setup cancelled"
        exit 0
    fi

    # Pre-flight check
    check_root

    # Run setup steps
    step_1_create_user
    step_2_setup_ssh
    step_3_install_git
    step_4_git_config
    step_5_github_ssh
    step_6_clone_repo
    step_7_next_steps
}

# Trap errors
trap 'print_error "An error occurred. Setup may be incomplete."; exit 1' ERR

# Run main
main "$@"

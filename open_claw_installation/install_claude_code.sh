#!/bin/bash

#############################################################################
# Claude Code Installation Script for Hostinger VPS
# Automates installation, tmux setup, and provides authentication guidance
#
# Usage:
#   chmod +x install_claude_code.sh
#   ./install_claude_code.sh
#
# What this script does:
#   1. Checks system requirements
#   2. Installs Claude Code CLI
#   3. Sets up tmux with optimal configuration
#   4. Provides authentication instructions
#   5. Tests installation
#############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
MIN_RAM_GB=4
CLAUDE_BIN="$HOME/.local/bin/claude"

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

print_step() {
    echo -e "${CYAN}➜ $1${NC}"
}

#############################################################################
# Prerequisite Checks
#############################################################################

check_system_requirements() {
    print_header "Checking System Requirements"

    # Check RAM
    TOTAL_RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    TOTAL_RAM_GB=$((TOTAL_RAM_KB / 1024 / 1024))

    print_info "Total RAM: ${TOTAL_RAM_GB}GB"

    if [ $TOTAL_RAM_GB -lt $MIN_RAM_GB ]; then
        print_warning "Recommended RAM: ${MIN_RAM_GB}GB or more"
        print_warning "You have: ${TOTAL_RAM_GB}GB"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "RAM requirement met: ${TOTAL_RAM_GB}GB"
    fi

    # Check disk space
    AVAILABLE_GB=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    print_info "Available disk space: ${AVAILABLE_GB}GB"

    if [ $AVAILABLE_GB -lt 2 ]; then
        print_error "Insufficient disk space. Need at least 2GB free."
        exit 1
    else
        print_success "Disk space adequate"
    fi

    # Check internet connectivity
    if ping -c 1 google.com &> /dev/null; then
        print_success "Internet connection verified"
    else
        print_error "No internet connection. Check network."
        exit 1
    fi

    # Check shell
    CURRENT_SHELL=$(basename "$SHELL")
    print_info "Current shell: $CURRENT_SHELL"

    if [[ "$CURRENT_SHELL" != "bash" && "$CURRENT_SHELL" != "zsh" ]]; then
        print_warning "Claude Code works best with Bash or Zsh"
    fi
}

check_claude_subscription() {
    print_header "Checking Claude Subscription"

    echo -e "${YELLOW}IMPORTANT: You need an active Claude subscription to use Claude Code${NC}\n"
    echo "Required: ONE of the following:"
    echo "  1. Claude Pro subscription (\$20/month)"
    echo "  2. Claude Max subscription (\$30/month)"
    echo "  3. Claude Console with active billing"
    echo "  4. Claude for Teams/Enterprise access"
    echo ""

    read -p "Do you have an active Claude subscription? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_error "Claude subscription required. Visit: https://console.anthropic.com/"
        print_info "Come back after subscribing!"
        exit 1
    fi

    print_success "Subscription confirmed"
}

#############################################################################
# Installation Steps
#############################################################################

step_1_install_claude_code() {
    print_header "Step 1: Installing Claude Code"

    # Check if already installed
    if [ -f "$CLAUDE_BIN" ]; then
        CURRENT_VERSION=$("$CLAUDE_BIN" --version 2>/dev/null || echo "unknown")
        print_warning "Claude Code already installed: $CURRENT_VERSION"
        read -p "Reinstall/Update? (Y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            print_info "Skipping installation"
            return
        fi
    fi

    # Create bin directory if doesn't exist
    mkdir -p "$HOME/.local/bin"

    print_step "Downloading and installing Claude Code..."

    # Run official installer
    if curl -fsSL https://claude.ai/install.sh | bash; then
        print_success "Claude Code installed successfully"
    else
        print_error "Installation failed"
        print_info "Trying alternative method..."

        # Alternative: direct download
        print_step "Downloading Claude Code binary..."
        wget -q https://github.com/anthropics/claude-code/releases/latest/download/claude-linux-x64 -O "$CLAUDE_BIN"
        chmod +x "$CLAUDE_BIN"
        print_success "Claude Code binary downloaded"
    fi

    # Add to PATH if not already
    if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
        print_step "Adding Claude Code to PATH..."

        # Determine which RC file to use
        if [ -f "$HOME/.bashrc" ]; then
            RC_FILE="$HOME/.bashrc"
        elif [ -f "$HOME/.zshrc" ]; then
            RC_FILE="$HOME/.zshrc"
        else
            RC_FILE="$HOME/.profile"
        fi

        echo '' >> "$RC_FILE"
        echo '# Claude Code' >> "$RC_FILE"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$RC_FILE"

        # Source immediately
        export PATH="$HOME/.local/bin:$PATH"

        print_success "PATH updated in $RC_FILE"
    fi

    # Verify installation
    print_step "Verifying installation..."

    if "$CLAUDE_BIN" --version &> /dev/null; then
        VERSION=$("$CLAUDE_BIN" --version)
        print_success "Installation verified: $VERSION"
    else
        print_error "Installation verification failed"
        print_info "Try running: source ~/.bashrc"
        exit 1
    fi
}

step_2_install_tmux() {
    print_header "Step 2: Installing and Configuring tmux"

    # Check if tmux is installed
    if command -v tmux &> /dev/null; then
        TMUX_VERSION=$(tmux -V)
        print_info "tmux already installed: $TMUX_VERSION"
    else
        print_step "Installing tmux..."

        if [ -f /etc/debian_version ]; then
            sudo apt update -qq
            sudo apt install -y tmux
        elif [ -f /etc/redhat-release ]; then
            sudo yum install -y tmux
        else
            print_error "Unsupported OS. Install tmux manually."
            return
        fi

        print_success "tmux installed"
    fi

    # Create tmux configuration
    print_step "Creating tmux configuration..."

    cat > "$HOME/.tmux.conf" <<'EOF'
# Claude Code tmux configuration

# Enable mouse support (scroll, select panes, resize)
set -g mouse on

# Increase scrollback buffer
set -g history-limit 10000

# Better colors
set -g default-terminal "screen-256color"

# Start window numbering at 1 (easier to reach)
set -g base-index 1
set -g pane-base-index 1

# Renumber windows when one is closed
set -g renumber-windows on

# Easy config reload
bind r source-file ~/.tmux.conf \; display "tmux config reloaded!"

# Split panes using | and - (more intuitive)
bind | split-window -h
bind - split-window -v
unbind '"'
unbind %

# Switch panes using Alt+arrow without prefix
bind -n M-Left select-pane -L
bind -n M-Right select-pane -R
bind -n M-Up select-pane -U
bind -n M-Down select-pane -D

# Quick pane switching with Ctrl+arrow
bind -n C-Left select-pane -L
bind -n C-Right select-pane -R
bind -n C-Up select-pane -U
bind -n C-Down select-pane -D

# Status bar styling
set -g status-bg colour235
set -g status-fg colour136
set -g status-left-length 20
set -g status-left '#{?client_prefix,#[fg=colour196],#[fg=colour76]}■ #S #[default]'
set -g status-right '#[fg=colour136]%H:%M %d-%b-%y'

# Pane border colors
set -g pane-border-style fg=colour240
set -g pane-active-border-style fg=colour76

# Message styling
set -g message-style bg=colour235,fg=colour166

# Activity monitoring
setw -g monitor-activity on
set -g visual-activity off

# Don't rename windows automatically
set -g allow-rename off

# Fix vim mode switching delay
set -s escape-time 0
EOF

    print_success "tmux configuration created"

    # Load configuration
    if tmux info &> /dev/null; then
        print_step "Reloading tmux configuration..."
        tmux source-file "$HOME/.tmux.conf" 2>/dev/null || true
    fi
}

step_3_authentication_guide() {
    print_header "Step 3: Authentication Setup"

    echo -e "${YELLOW}Claude Code requires authentication via browser.${NC}"
    echo -e "${YELLOW}Since this is a VPS (no GUI), we'll use SSH port forwarding.${NC}\n"

    echo -e "${CYAN}Authentication Method: SSH Port Forwarding${NC}\n"

    echo "Here's what you'll do:"
    echo ""
    echo "1. On VPS (this terminal):"
    echo -e "   ${GREEN}claude /login${NC}"
    echo ""
    echo "2. Copy the URL shown (e.g., http://localhost:12345/auth?code=...)"
    echo ""
    echo "3. Note the PORT number (e.g., 12345)"
    echo ""
    echo "4. In a NEW terminal on your LOCAL machine, create SSH tunnel:"
    echo -e "   ${GREEN}ssh -L PORT:localhost:PORT $(whoami)@$(hostname -I | awk '{print $1}')${NC}"
    echo "   (Replace PORT with the actual number)"
    echo ""
    echo "5. Open the copied URL in your LOCAL browser"
    echo ""
    echo "6. Log in to Claude and authorize"
    echo ""
    echo "7. Return to VPS terminal - authentication will complete automatically"
    echo ""

    print_info "This needs to be done only ONCE (credentials persist)"

    echo ""
    read -p "Ready to authenticate now? (Y/n): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_step "Starting authentication..."
        print_warning "Remember: Open SSH tunnel on LOCAL machine when prompted!"
        echo ""

        # Run login
        "$CLAUDE_BIN" /login || {
            print_error "Authentication failed or was cancelled"
            print_info "You can retry later with: claude /login"
            return
        }

        print_success "Authentication completed!"
    else
        print_info "You can authenticate later with: claude /login"
    fi
}

step_4_create_helper_scripts() {
    print_header "Step 4: Creating Helper Scripts"

    # Create start script
    print_step "Creating claude-start script..."

    cat > "$HOME/.local/bin/claude-start" <<'EOF'
#!/bin/bash
# Start Claude Code in persistent tmux session

SESSION_NAME="claude"

if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "Claude session already exists. Attaching..."
    tmux attach -t $SESSION_NAME
else
    echo "Creating new Claude session..."
    tmux new -s $SESSION_NAME -n claude "claude"
fi
EOF

    chmod +x "$HOME/.local/bin/claude-start"
    print_success "claude-start script created"

    # Create helper script for auth
    print_step "Creating claude-auth-help script..."

    cat > "$HOME/.local/bin/claude-auth-help" <<EOF
#!/bin/bash
# Display authentication help

echo "═══════════════════════════════════════"
echo "Claude Code Authentication Helper"
echo "═══════════════════════════════════════"
echo ""
echo "Step 1: On this VPS, run:"
echo "  claude /login"
echo ""
echo "Step 2: Copy the URL and note the PORT"
echo ""
echo "Step 3: On your LOCAL computer, run:"
echo "  ssh -L PORT:localhost:PORT $(whoami)@$(hostname -I | awk '{print $1}')"
echo ""
echo "Step 4: Open the URL in your LOCAL browser"
echo ""
echo "Step 5: Log in and authorize"
echo ""
echo "═══════════════════════════════════════"
EOF

    chmod +x "$HOME/.local/bin/claude-auth-help"
    print_success "claude-auth-help script created"

    # Create tmux quick reference
    print_step "Creating tmux-help script..."

    cat > "$HOME/.local/bin/tmux-help" <<'EOF'
#!/bin/bash
# Quick tmux reference for Claude Code

echo "═══════════════════════════════════════"
echo "tmux Quick Reference"
echo "═══════════════════════════════════════"
echo ""
echo "Session Management:"
echo "  Start Claude:     claude-start"
echo "  Detach:           Ctrl+B then D"
echo "  List sessions:    tmux ls"
echo "  Attach:           tmux attach -t claude"
echo "  Kill session:     tmux kill-session -t claude"
echo ""
echo "Inside tmux:"
echo "  Split vertical:   Ctrl+B then |"
echo "  Split horizontal: Ctrl+B then -"
echo "  Switch panes:     Ctrl+Arrow keys"
echo "  Scroll mode:      Ctrl+B then [ (q to exit)"
echo "  Reload config:    Ctrl+B then r"
echo ""
echo "═══════════════════════════════════════"
EOF

    chmod +x "$HOME/.local/bin/tmux-help"
    print_success "tmux-help script created"
}

step_5_verification() {
    print_header "Step 5: Installation Verification"

    # Check Claude Code
    print_step "Checking Claude Code..."
    if "$CLAUDE_BIN" --version &> /dev/null; then
        VERSION=$("$CLAUDE_BIN" --version)
        print_success "Claude Code: $VERSION"
    else
        print_error "Claude Code not accessible"
    fi

    # Check tmux
    print_step "Checking tmux..."
    if command -v tmux &> /dev/null; then
        TMUX_VERSION=$(tmux -V)
        print_success "tmux: $TMUX_VERSION"
    else
        print_warning "tmux not found"
    fi

    # Check authentication
    print_step "Checking authentication..."
    if [ -f "$HOME/.config/claude-code/auth.json" ]; then
        print_success "Authentication file found"
    else
        print_warning "Not authenticated yet"
        print_info "Run: claude /login"
    fi

    # Test Claude (if authenticated)
    if [ -f "$HOME/.config/claude-code/auth.json" ]; then
        print_step "Testing Claude Code..."
        if echo "hello" | timeout 10 "$CLAUDE_BIN" "respond with just 'Hi!'" &> /dev/null; then
            print_success "Claude Code working!"
        else
            print_warning "Could not test (timeout or not authenticated)"
        fi
    fi
}

display_completion_info() {
    clear

    cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         Claude Code Installation Complete! 🎉            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF

    echo ""
    echo -e "${GREEN}✓ Claude Code CLI installed${NC}"
    echo -e "${GREEN}✓ tmux configured for persistent sessions${NC}"
    echo -e "${GREEN}✓ Helper scripts created${NC}"
    echo ""

    echo -e "${BLUE}Quick Start Commands:${NC}"
    echo ""
    echo -e "  ${CYAN}claude-start${NC}         Start Claude in tmux session"
    echo -e "  ${CYAN}claude 'your query'${NC}  One-off command"
    echo -e "  ${CYAN}claude-auth-help${NC}     Authentication instructions"
    echo -e "  ${CYAN}tmux-help${NC}            tmux quick reference"
    echo ""

    echo -e "${BLUE}Authentication:${NC}"
    if [ -f "$HOME/.config/claude-code/auth.json" ]; then
        echo -e "  ${GREEN}✓ Already authenticated${NC}"
    else
        echo -e "  ${YELLOW}⚠ Not authenticated yet${NC}"
        echo -e "  Run: ${CYAN}claude /login${NC}"
        echo -e "  Or:  ${CYAN}claude-auth-help${NC} for detailed instructions"
    fi
    echo ""

    echo -e "${BLUE}Next Steps:${NC}"
    echo "  1. Authenticate (if not done): claude /login"
    echo "  2. Start Claude in tmux: claude-start"
    echo "  3. Try a command: claude 'introduce yourself'"
    echo "  4. Detach from tmux: Ctrl+B then D"
    echo "  5. Reattach anytime: claude-start"
    echo ""

    echo -e "${BLUE}Documentation:${NC}"
    echo "  Full guide: CLAUDE_CODE_INSTALLATION.md"
    echo "  Online: https://code.claude.com/docs/"
    echo ""

    echo -e "${BLUE}Helper Scripts:${NC}"
    echo "  claude-start      - Start Claude in persistent tmux"
    echo "  claude-auth-help  - Show authentication instructions"
    echo "  tmux-help         - tmux quick reference"
    echo ""

    echo -e "${GREEN}Happy coding with Claude! 🚀${NC}"
    echo ""
}

#############################################################################
# Main Installation Flow
#############################################################################

main() {
    clear

    cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        _____ _                 _        _____             ║
║       / ____| |               | |      / ____|            ║
║      | |    | | __ _ _   _  __| | ___ | |     ___   __   ║
║      | |    | |/ _` | | | |/ _` |/ _ \| |    / _ \ / _`  ║
║      | |____| | (_| | |_| | (_| |  __/| |___| (_) | (_|  ║
║       \_____|_|\__,_|\__,_|\__,_|\___| \_____\___/ \__,  ║
║                                                       |_|  ║
║                                                           ║
║          Installation Script for Hostinger VPS           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF

    echo -e "\n${BLUE}This script will install Claude Code on your Ubuntu VPS${NC}"
    echo -e "${BLUE}and set up tmux for persistent sessions.${NC}\n"

    read -p "Continue with installation? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Installation cancelled"
        exit 0
    fi

    # Run installation steps
    check_system_requirements
    check_claude_subscription
    step_1_install_claude_code
    step_2_install_tmux
    step_3_authentication_guide
    step_4_create_helper_scripts
    step_5_verification
    display_completion_info
}

# Trap errors
trap 'print_error "An error occurred. Installation may be incomplete."; exit 1' ERR

# Run main installation
main "$@"

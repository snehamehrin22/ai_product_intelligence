#!/bin/bash
#
# Ralph Agent Loop - Simple autonomous executor for PRD-driven development
#
# Based on loop engineering patterns (2025-2026):
# - Bounded execution with max iterations
# - Clear stopping conditions
# - Observability through logging
# - Human-in-the-loop safety gates
#
# Usage:
#   ./scripts/ralph.sh                    # Interactive mode with approval gates
#   ./scripts/ralph.sh --auto             # Autonomous mode (no approval)
#   ./scripts/ralph.sh --max-iter 10      # Custom max iterations
#

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PRD_PATH="${PRD_PATH:-$PROJECT_ROOT/ai-todo-app/prd-phase-2.json}"
PROGRESS_FILE="${PROJECT_ROOT}/progress-phase-2.txt"
LOG_DIR="${PROJECT_ROOT}/logs"
LOG_FILE="${LOG_DIR}/ralph_$(date +%Y%m%d_%H%M%S).log"

MAX_ITERATIONS=50
AUTO_APPROVE=false
ITERATION=0
COMPLETED_STORIES=0
FAILED_STORIES=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================================
# Parse Arguments
# ============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --auto)
            AUTO_APPROVE=true
            shift
            ;;
        --max-iter)
            MAX_ITERATIONS="$2"
            shift 2
            ;;
        --prd)
            PRD_PATH="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --auto           Auto-approve all actions (no prompts)"
            echo "  --max-iter N     Maximum loop iterations (default: 50)"
            echo "  --prd PATH       Path to prd.json (default: ai-todo-app/prd-phase-2.json)"
            echo "  -h, --help       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# ============================================================================
# Setup
# ============================================================================

mkdir -p "$LOG_DIR"

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log_info() {
    log "${CYAN}[INFO]${NC} $1"
}

log_success() {
    log "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    log "${RED}[ERROR]${NC} $1"
}

log_warning() {
    log "${YELLOW}[WARNING]${NC} $1"
}

header() {
    log ""
    log "${BLUE}================================================================================${NC}"
    log "${BLUE}$1${NC}"
    log "${BLUE}================================================================================${NC}"
    log ""
}

# ============================================================================
# Helper Functions
# ============================================================================

check_dependencies() {
    if ! command -v jq &> /dev/null; then
        log_error "jq is not installed. Install with: brew install jq"
        exit 1
    fi

    if [ ! -f "$PRD_PATH" ]; then
        log_error "PRD not found: $PRD_PATH"
        exit 1
    fi
}

get_incomplete_story() {
    # Find highest priority incomplete story with met dependencies
    jq -r '.userStories[] | select(.passes == false) | "\(.priority)|\(.id)|\(.title)"' "$PRD_PATH" | \
        sort | head -1
}

get_total_stories() {
    jq '.userStories | length' "$PRD_PATH"
}

get_completed_count() {
    jq '[.userStories[] | select(.passes == true)] | length' "$PRD_PATH"
}

mark_story_complete() {
    local story_id="$1"

    # Update PRD using jq
    jq --arg id "$story_id" \
        '(.userStories[] | select(.id == $id) | .passes) = true' \
        "$PRD_PATH" > "${PRD_PATH}.tmp" && mv "${PRD_PATH}.tmp" "$PRD_PATH"
}

get_story_details() {
    local story_id="$1"
    jq --arg id "$story_id" '.userStories[] | select(.id == $id)' "$PRD_PATH"
}

run_quality_checks() {
    log_info "Running quality checks..."

    # Backend checks if backend exists
    if [ -d "$PROJECT_ROOT/ai-todo-app/backend" ]; then
        log_info "Checking backend..."
        cd "$PROJECT_ROOT/ai-todo-app/backend"

        if [ -f ".venv/bin/activate" ]; then
            source .venv/bin/activate

            # Format check
            if command -v black &> /dev/null; then
                log_info "Running black..."
                black app/ || return 1
            fi

            # Lint check
            if command -v ruff &> /dev/null; then
                log_info "Running ruff..."
                ruff check app/ --fix || return 1
            fi

            # Tests
            if [ -d "tests" ]; then
                log_info "Running pytest..."
                pytest || return 1
            fi
        fi
    fi

    # Frontend checks if frontend exists
    if [ -d "$PROJECT_ROOT/ai-todo-app/frontend" ]; then
        log_info "Checking frontend..."
        cd "$PROJECT_ROOT/ai-todo-app/frontend"

        if [ -f "package.json" ]; then
            # Type check
            if npm run typecheck &> /dev/null; then
                log_info "Running type check..."
                npm run typecheck || return 1
            fi

            # Lint
            if npm run lint &> /dev/null; then
                log_info "Running linter..."
                npm run lint || return 1
            fi
        fi
    fi

    cd "$PROJECT_ROOT"
    return 0
}

git_commit_changes() {
    local story_id="$1"
    local story_title="$2"

    log_info "Committing changes..."

    cd "$PROJECT_ROOT/ai-todo-app"

    git add .

    if git diff --cached --quiet; then
        log_warning "No changes to commit (already committed?)"
        return 0
    fi

    local commit_msg="feat: ${story_id} - ${story_title}"

    git commit -m "$commit_msg"

    log_success "Committed: $commit_msg"
}

append_progress() {
    local story_id="$1"
    local story_title="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    cat >> "$PROGRESS_FILE" <<EOF

## $timestamp - $story_id
- **Story:** $story_title
- **Status:** ✅ Complete
- **Iteration:** $ITERATION
- **Learnings:** See commit message and CLAUDE.md updates
---
EOF
}

prompt_user() {
    if [ "$AUTO_APPROVE" = true ]; then
        return 0
    fi

    echo -ne "${YELLOW}Continue? [Y/n]:${NC} "
    read -r response

    if [[ "$response" =~ ^[Nn]$ ]]; then
        return 1
    fi

    return 0
}

# ============================================================================
# Main Loop
# ============================================================================

main() {
    header "🚀 Ralph Agent Loop - PRD Autonomous Executor"

    check_dependencies

    log_info "PRD: $PRD_PATH"
    log_info "Max iterations: $MAX_ITERATIONS"
    log_info "Auto-approve: $AUTO_APPROVE"
    log_info "Log file: $LOG_FILE"

    local start_time=$(date +%s)

    # Main execution loop
    while [ $ITERATION -lt $MAX_ITERATIONS ]; do
        ITERATION=$((ITERATION + 1))

        header "🔄 Iteration $ITERATION/$MAX_ITERATIONS"

        # Get next story
        local story_info=$(get_incomplete_story)

        if [ -z "$story_info" ]; then
            log_success "No incomplete stories found!"
            header "🎉 ALL STORIES COMPLETE!"
            break
        fi

        # Parse story info
        local priority=$(echo "$story_info" | cut -d'|' -f1)
        local story_id=$(echo "$story_info" | cut -d'|' -f2)
        local story_title=$(echo "$story_info" | cut -d'|' -f3)

        log_info "Story: $story_id - $story_title"
        log_info "Priority: $priority"

        # Show story details
        local story_json=$(get_story_details "$story_id")
        log ""
        log "Acceptance Criteria:"
        echo "$story_json" | jq -r '.acceptanceCriteria[] | "  - \(.)"' | tee -a "$LOG_FILE"
        log ""

        # Prompt user if not auto-approved
        if ! prompt_user; then
            log_warning "Skipped by user"
            break
        fi

        # Execute story with Claude Code
        log_info "🤖 Invoking Claude Code to implement $story_id..."
        log_info "This may take several minutes..."
        log ""

        # Build prompt for Claude
        local claude_prompt="Implement user story $story_id according to the PRD at $PRD_PATH. Follow the Ralph Agent Instructions in CLAUDE.md. Work autonomously until the story is complete, tested, and committed."

        # Call Claude Code (using echo to pipe prompt)
        if echo "$claude_prompt" | claude code --cwd "$PROJECT_ROOT/ai-todo-app" 2>&1 | tee -a "$LOG_FILE"; then
            log_success "Story execution completed"

            # Run quality checks
            if run_quality_checks; then
                log_success "Quality checks passed"

                # Commit if not already committed
                if ! git diff --cached --quiet 2>/dev/null; then
                    git_commit_changes "$story_id" "$story_title"
                fi

                # Mark complete in PRD
                mark_story_complete "$story_id"

                # Log progress
                append_progress "$story_id" "$story_title"

                COMPLETED_STORIES=$((COMPLETED_STORIES + 1))

                log_success "Story $story_id marked complete ✅"
            else
                log_error "Quality checks failed"
                FAILED_STORIES=$((FAILED_STORIES + 1))
            fi
        else
            log_error "Story execution failed"
            FAILED_STORIES=$((FAILED_STORIES + 1))
        fi

        # Show progress
        local total=$(get_total_stories)
        local completed=$(get_completed_count)
        log_info "Progress: $completed/$total stories complete"
        log ""
    done

    # Summary
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    header "📊 EXECUTION SUMMARY"
    log_info "Total iterations: $ITERATION"
    log_info "Stories completed: $COMPLETED_STORIES"
    log_info "Stories failed: $FAILED_STORIES"
    log_info "Total time: ${duration}s"
    log_info "Log file: $LOG_FILE"
    log ""

    if [ $ITERATION -ge $MAX_ITERATIONS ]; then
        log_warning "Reached max iterations ($MAX_ITERATIONS). Stopping for safety."
        exit 1
    fi

    if [ $(get_completed_count) -eq $(get_total_stories) ]; then
        log_success "🎉 ALL STORIES COMPLETE! 🎉"
        exit 0
    else
        log_warning "Loop stopped before completion"
        exit 1
    fi
}

# ============================================================================
# Entry Point
# ============================================================================

main "$@"

#!/usr/bin/env bash
# Agent Coordinator for multi-agent workflow
# Usage: ./coordinate.sh init              - Set up directories
#        ./coordinate.sh list              - List available agents
#        ./coordinate.sh workflow          - Show TDD workflow
#        ./coordinate.sh worktree <cmd>    - Manage worktrees for isolation
# Or manually invoke agents in Claude Code with @agent-name syntax

set -e

COMMAND="${1:-help}"
SUBCOMMAND="${2:-}"
ARG3="${3:-}"

# Colour codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Colour

# Worktree configuration
WORKTREE_BASE=".worktrees"
DOMAINS=("discovery" "design" "backend" "frontend" "review" "infra" "docs")

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_phase() {
    echo -e "${CYAN}[PHASE]${NC} $1"
}

# Check if artefacts directory exists
ensure_artefacts_dir() {
    if [ ! -d "./artefacts" ]; then
        log_warning "Creating ./artefacts directory"
        mkdir -p ./artefacts
    fi
}

# Create subdirectories for each agent's work
init_agent_dirs() {
    ensure_artefacts_dir

    log_info "Initialising agent directories..."

    # Phase 0: Discovery
    # (files created directly in ./artefacts/)

    # Phase 1: Design
    mkdir -p ./artefacts/database/migrations
    mkdir -p ./artefacts/api
    mkdir -p ./artefacts/design/visuals

    # Phase 2-3: Development
    mkdir -p ./artefacts/python/tests
    mkdir -p ./artefacts/typescript/tests

    # Phase 4-5: Testing
    mkdir -p ./artefacts/test-results
    mkdir -p ./artefacts/ui-test-results/screenshots
    mkdir -p ./artefacts/security-audit

    # Phase 6: Deploy
    mkdir -p ./artefacts/gcp/terraform

    # Phase 7: Documentation (per doc-standards.md)
    mkdir -p ./artefacts/context/build
    mkdir -p ./artefacts/context/specs
    mkdir -p ./artefacts/context/guides

    # Create requirements template if not present
    if [ ! -f "./artefacts/requirements.md" ]; then
        cat > ./artefacts/requirements.md << 'EOF'
# Project Requirements

## Overview
Define your project requirements, acceptance criteria, and constraints here.

## Acceptance Criteria
- [ ] Component 1
- [ ] Component 2

## Technical Constraints
- Python 3.10+
- TypeScript with strict mode
- pytest for testing
- GCP Cloud Run for hosting

## API Contract
See ./artefacts/api-contract.json for interface definitions.
EOF
        log_success "Created requirements.md template"
    fi

    log_success "Agent environment initialised"
}

# List available agents by phase
list_agents() {
    echo ""
    log_phase "Phase 0: Discovery (domain: discovery)"
    echo "  @product-owner       - Requirements gathering and user stories"
    echo ""

    log_phase "Phase 1: Design (domain: design)"
    echo "  @solution-architect  - System architecture and API contracts"
    echo "  @database-designer   - Database schema and migrations"
    echo "  @api-designer        - OpenAPI specifications"
    echo "  @ui-designer         - UI wireframes, components, design tokens"
    echo "  @visual-designer     - Visual assets using AI tools"
    echo ""

    log_phase "Phase 2: Tests First (domain: backend/frontend)"
    echo "  @functional-tester   - Write failing tests from requirements"
    echo ""

    log_phase "Phase 3: Development (domain: backend/frontend)"
    echo "  @python-coder        - Write Python code to pass tests"
    echo "  @typescript-coder    - Write TypeScript code to pass tests"
    echo ""

    log_phase "Phase 4: Review (domain: review)"
    echo "  @tech-lead           - Architecture compliance gate"
    echo "  @code-reviewer       - Deep bug hunting"
    echo ""

    log_phase "Phase 5: Testing (domain: review)"
    echo "  @functional-tester   - Run all tests, verify coverage"
    echo "  @ui-tester           - Test UI with Chrome DevTools"
    echo "  @security-tester     - Security audit and threat modelling"
    echo ""

    log_phase "Phase 6: Deploy (domain: infra)"
    echo "  @gcp-devops          - Configure GCP infrastructure"
    echo ""

    log_phase "Phase 7: Documentation (domain: docs)"
    echo "  @documentation       - API references and guides"
    echo ""

    echo "Usage in Claude Code:"
    echo "  @product-owner define requirements for a task management API"
    echo "  @functional-tester write failing tests for the task API"
    echo "  @python-coder implement the task service (make tests pass)"
}

# Show TDD workflow
show_workflow() {
    cat << 'EOF'

TDD WORKFLOW (Test-Driven Development)
======================================

Tests are written BEFORE implementation.

Phase 0: Discovery
    @product-owner
    Output: requirements.md, user-stories.md, open-questions.md
                |
                v
Phase 1: Design (parallel)
    @solution-architect  -> architecture.md, api-contract.json
    @database-designer   -> schema.sql, migrations/
    @api-designer        -> openapi.yaml
    @ui-designer         -> design-system.md
    @visual-designer     -> design/visuals/
                |
                v
Phase 2: Tests First (TDD RED)
    @functional-tester
    Output: Failing tests based on requirements
    All tests SHOULD FAIL initially
                |
                v
Phase 3: Development (TDD GREEN)
    @python-coder        -> ./artefacts/python/
    @typescript-coder    -> ./artefacts/typescript/
    Goal: Make all tests pass
                |
                v
Phase 4: Review (GATE)
    @tech-lead reviews (architecture, standards)
        |
        +-- CHANGES REQUIRED --> Back to Phase 3
        |
        +-- APPROVED --> @code-reviewer (bugs, edge cases)
                |
                v
Phase 5: Testing (parallel)
    @functional-tester   -> coverage report
    @ui-tester           -> ui-test-results/
    @security-tester     -> security-audit/
                |
                v
Phase 6: Deploy
    @gcp-devops          -> gcp/terraform/
                |
                v
Phase 7: Documentation
    @documentation       -> context/

COVERAGE REQUIREMENTS
=====================
Minimum: 90% (build fails below)
Target:  100%
Gaps:    Document in test-gaps.md

TDD CYCLE
=========
1. RED:    @functional-tester writes failing tests
2. GREEN:  @python-coder/@typescript-coder makes tests pass
3. REFACTOR: Clean up while tests pass
4. REPEAT: Next requirement

EOF
}

# Show artefacts directory structure
show_structure() {
    cat << 'EOF'

ARTIFACTS DIRECTORY STRUCTURE
=============================

./artefacts/
├── requirements.md              # Product owner
├── user-stories.md              # Product owner
├── open-questions.md            # Product owner
├── architecture.md              # Solution architect
├── api-contract.json            # Solution architect
├── data-model.md                # Solution architect
├── database/
│   ├── schema.sql               # Database designer
│   ├── migrations/              # Database designer
│   └── er-diagram.md            # Database designer
├── api/
│   ├── openapi.yaml             # API designer
│   └── api-design-guide.md      # API designer
├── design/
│   ├── design-system.md        # UI designer (tokens, components, accessibility, wireframes)
│   └── visuals/                 # Visual designer
├── python/
│   ├── *.py                     # Python coder
│   ├── requirements.txt
│   ├── README.md
│   └── tests/                   # Functional tester
├── typescript/
│   ├── *.ts                     # TypeScript coder
│   ├── package.json
│   ├── README.md
│   └── tests/                   # Functional tester
├── test-results/                # Functional tester
├── test-gaps.md                 # Functional tester (if coverage < 100%)
├── ui-test-results/             # UI tester
│   └── screenshots/
├── security-audit/              # Security tester
│   └── prompt-injection-assessment.md
├── gcp/
│   └── terraform/               # GCP DevOps
├── tech-review.md               # Tech lead
├── code-review.md               # Code reviewer
└── context/                        # Documentation (per doc-standards.md)
    ├── build/
    │   ├── bugs.md              # Bug tracking
    │   ├── tasks.md             # Task tracking
    │   └── todo.md              # Technical debt
    ├── specs/
    │   ├── product.md           # Product/UX docs
    │   ├── requirements.md      # EARS requirements
    │   └── design.md            # Architecture decisions
    └── guides/
        ├── getting-started.md   # Setup guide
        └── developer-guide.md   # Dev workflows

EOF
}

# =============================================================================
# WORKTREE MANAGEMENT
# =============================================================================

# Create all worktrees for a feature
worktree_create() {
    local feature_name="$1"

    if [ -z "$feature_name" ]; then
        log_error "Feature name required: ./coordinate.sh worktree create <feature-name>"
        exit 1
    fi

    log_info "Creating worktrees for feature: $feature_name"

    # Ensure we're in a git repo
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not a git repository"
        exit 1
    fi

    # Create worktree base directory
    mkdir -p "$WORKTREE_BASE"

    # Get current branch as base
    local base_branch
    base_branch=$(git branch --show-current)

    # Create a worktree for each domain
    for domain in "${DOMAINS[@]}"; do
        local branch_name="feature/${feature_name}/${domain}"
        local worktree_path="${WORKTREE_BASE}/${domain}"

        if [ -d "$worktree_path" ]; then
            log_warning "Worktree already exists: $worktree_path"
            continue
        fi

        log_info "Creating branch and worktree: $domain"

        # Create branch from current HEAD
        git branch "$branch_name" 2>/dev/null || true

        # Create worktree
        git worktree add "$worktree_path" "$branch_name"

        # Initialise artefacts in the worktree
        (cd "$worktree_path" && mkdir -p ./artefacts)

        log_success "Created: $worktree_path -> $branch_name"
    done

    # Create tracking file to remember feature name
    echo "$feature_name" > "${WORKTREE_BASE}/.feature"

    log_success "All worktrees created for feature: $feature_name"
    echo ""
    echo "Next steps:"
    echo "  ./coordinate.sh worktree switch discovery"
    echo "  @product-owner define requirements..."
}

# List all worktrees
worktree_list() {
    log_info "Active worktrees:"
    echo ""
    git worktree list
    echo ""

    if [ -f "${WORKTREE_BASE}/.feature" ]; then
        local feature_name
        feature_name=$(cat "${WORKTREE_BASE}/.feature")
        log_info "Current feature: $feature_name"
    fi

    echo ""
    log_info "Context domains:"
    for domain in "${DOMAINS[@]}"; do
        local worktree_path="${WORKTREE_BASE}/${domain}"
        if [ -d "$worktree_path" ]; then
            local branch
            branch=$(cd "$worktree_path" && git branch --show-current)
            echo "  ${GREEN}✓${NC} $domain -> $branch"
        else
            echo "  ${YELLOW}○${NC} $domain (not created)"
        fi
    done
}

# Switch to a domain's worktree
worktree_switch() {
    local domain="$1"

    if [ -z "$domain" ]; then
        log_error "Domain required: ./coordinate.sh worktree switch <domain>"
        echo "Available domains: ${DOMAINS[*]}"
        exit 1
    fi

    local worktree_path="${WORKTREE_BASE}/${domain}"

    if [ ! -d "$worktree_path" ]; then
        log_error "Worktree does not exist: $worktree_path"
        log_info "Create worktrees first: ./coordinate.sh worktree create <feature-name>"
        exit 1
    fi

    log_info "Switching to domain: $domain"
    log_info "Path: $worktree_path"
    echo ""
    echo "Run: cd $worktree_path"
    echo ""

    # Print domain-specific agents
    case "$domain" in
        discovery)
            echo "Agents in this domain: @product-owner"
            ;;
        design)
            echo "Agents in this domain: @solution-architect, @database-designer, @api-designer, @ui-designer, @visual-designer"
            ;;
        backend)
            echo "Agents in this domain: @python-coder, @functional-tester (Python)"
            ;;
        frontend)
            echo "Agents in this domain: @typescript-coder, @functional-tester (TypeScript)"
            ;;
        review)
            echo "Agents in this domain: @tech-lead, @code-reviewer, @security-tester"
            ;;
        infra)
            echo "Agents in this domain: @gcp-devops"
            ;;
        docs)
            echo "Agents in this domain: @documentation"
            ;;
    esac
}

# Sync worktree with main
worktree_sync() {
    local domain="$1"

    if [ -z "$domain" ]; then
        log_error "Domain required: ./coordinate.sh worktree sync <domain>"
        exit 1
    fi

    local worktree_path="${WORKTREE_BASE}/${domain}"

    if [ ! -d "$worktree_path" ]; then
        log_error "Worktree does not exist: $worktree_path"
        exit 1
    fi

    log_info "Syncing $domain with main..."

    (
        cd "$worktree_path"
        git fetch origin main
        git merge origin/main --no-edit
    )

    log_success "Synced $domain with latest main"
}

# Create PR from a domain
worktree_pr() {
    local domain="$1"
    local title="$2"

    if [ -z "$domain" ]; then
        log_error "Domain required: ./coordinate.sh worktree pr <domain> \"PR title\""
        exit 1
    fi

    local worktree_path="${WORKTREE_BASE}/${domain}"

    if [ ! -d "$worktree_path" ]; then
        log_error "Worktree does not exist: $worktree_path"
        exit 1
    fi

    if [ -z "$title" ]; then
        title="[$domain] Domain work complete"
    fi

    log_info "Creating PR for domain: $domain"

    (
        cd "$worktree_path"

        # Push branch
        local branch
        branch=$(git branch --show-current)
        git push -u origin "$branch"

        # Create PR using gh CLI
        if command -v gh &> /dev/null; then
            gh pr create --title "$title" --body "## Domain: $domain

This PR contains work from the $domain context domain.

### Reviewers
- [ ] Human approval required
- [ ] Domain-specific review (see agent-standards.md section 5.5)

### Context
See \`./artefacts/\` for domain outputs.
"
        else
            log_warning "gh CLI not installed. Push complete, create PR manually."
            echo "Branch pushed: $branch"
        fi
    )
}

# Cleanup worktrees after final PR
worktree_cleanup() {
    local feature_name="$1"

    if [ -z "$feature_name" ]; then
        if [ -f "${WORKTREE_BASE}/.feature" ]; then
            feature_name=$(cat "${WORKTREE_BASE}/.feature")
        else
            log_error "Feature name required: ./coordinate.sh worktree cleanup <feature-name>"
            exit 1
        fi
    fi

    log_warning "This will remove all worktrees and branches for: $feature_name"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleanup cancelled"
        exit 0
    fi

    log_info "Cleaning up feature: $feature_name"

    for domain in "${DOMAINS[@]}"; do
        local worktree_path="${WORKTREE_BASE}/${domain}"
        local branch_name="feature/${feature_name}/${domain}"

        if [ -d "$worktree_path" ]; then
            log_info "Removing worktree: $domain"
            git worktree remove "$worktree_path" --force 2>/dev/null || true
        fi

        # Delete local branch
        git branch -D "$branch_name" 2>/dev/null || true

        # Delete remote branch
        git push origin --delete "$branch_name" 2>/dev/null || true
    done

    # Remove tracking file
    rm -f "${WORKTREE_BASE}/.feature"

    # Remove worktree base if empty
    rmdir "$WORKTREE_BASE" 2>/dev/null || true

    log_success "Cleanup complete for: $feature_name"
}

# Show worktree help
worktree_help() {
    cat << 'EOF'

WORKTREE COMMANDS
=================

Worktrees provide isolation between context domains, limiting the blast radius
of agent changes and enabling parallel work.

Commands:
  ./coordinate.sh worktree create <feature>  Create worktrees for all domains
  ./coordinate.sh worktree list              List active worktrees
  ./coordinate.sh worktree switch <domain>   Show how to switch to a domain
  ./coordinate.sh worktree sync <domain>     Pull latest main into worktree
  ./coordinate.sh worktree pr <domain> "msg" Create PR from domain branch
  ./coordinate.sh worktree cleanup <feature> Remove all worktrees and branches

Domains:
  discovery  - @product-owner
  design     - @solution-architect, @database-designer, @api-designer, @ui-designer
  backend    - @python-coder, @functional-tester (Python)
  frontend   - @typescript-coder, @functional-tester (TypeScript)
  review     - @tech-lead, @code-reviewer, @security-tester
  infra      - @gcp-devops
  docs       - @documentation

Example workflow:
  ./coordinate.sh worktree create auth-feature
  cd .worktrees/discovery && @product-owner define requirements
  ./coordinate.sh worktree pr discovery "Requirements complete"
  # After PR merged...
  ./coordinate.sh worktree sync design
  cd .worktrees/design && @solution-architect design system
  ...continue through domains...
  ./coordinate.sh worktree cleanup auth-feature  # After final PR

See context/standards/agent-standards.md section 5 for full documentation.

EOF
}

# Worktree subcommand router
handle_worktree() {
    case "$SUBCOMMAND" in
        create)
            worktree_create "$ARG3"
            ;;
        list|ls)
            worktree_list
            ;;
        switch|sw)
            worktree_switch "$ARG3"
            ;;
        sync)
            worktree_sync "$ARG3"
            ;;
        pr)
            worktree_pr "$ARG3" "${4:-}"
            ;;
        cleanup|clean)
            worktree_cleanup "$ARG3"
            ;;
        *)
            worktree_help
            ;;
    esac
}

# =============================================================================
# MAIN
# =============================================================================

show_help() {
    cat << 'EOF'
Agent Coordinator - Multi-agent TDD orchestration for Claude Code

Usage:
  ./coordinate.sh init              - Initialise agent directories
  ./coordinate.sh list              - List available agents by phase
  ./coordinate.sh workflow          - Show TDD workflow
  ./coordinate.sh structure         - Show artefacts directory structure
  ./coordinate.sh worktree <cmd>    - Manage worktrees for domain isolation

Worktree commands:
  ./coordinate.sh worktree create <feature>  - Create all domain worktrees
  ./coordinate.sh worktree list              - List active worktrees
  ./coordinate.sh worktree switch <domain>   - Switch to a domain
  ./coordinate.sh worktree sync <domain>     - Sync with main
  ./coordinate.sh worktree pr <domain>       - Create PR from domain
  ./coordinate.sh worktree cleanup           - Remove worktrees after merge

In Claude Code, invoke agents directly:
  @product-owner define requirements for a task API
  @functional-tester write failing tests for the task API
  @python-coder implement the task service

See CLAUDE.md for full orchestration guide.
See context/standards/agent-standards.md section 5 for worktree isolation.
EOF
}

main() {
    case "$COMMAND" in
        list|--list|-l)
            list_agents
            ;;
        workflow|--workflow|-w)
            show_workflow
            ;;
        structure|--structure|-s)
            show_structure
            ;;
        init|--init|-i)
            init_agent_dirs
            ;;
        worktree|wt)
            handle_worktree
            ;;
        help|--help|-h|*)
            show_help
            ;;
    esac
}

main "$@"

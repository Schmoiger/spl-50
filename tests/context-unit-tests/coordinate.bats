#!/usr/bin/env bats
# Tests for coordinate.sh
# Requires: bats-core (brew install bats-core)
#
# Run with: bats tests/shell/coordinate.bats

setup() {
    # Get the directory of the test file
    TEST_DIR="$( cd "$( dirname "$BATS_TEST_FILENAME" )" && pwd )"
    PROJECT_ROOT="$TEST_DIR/../.."
    SCRIPT="$PROJECT_ROOT/context/agents/coordinate.sh"

    # Create a temp directory for test isolation
    TEMP_DIR="$(mktemp -d)"
    cd "$TEMP_DIR"

    # Initialise a git repo for worktree tests
    git init --quiet
    git config user.email "test@test.com"
    git config user.name "Test"
    echo "test" > test.txt
    git add test.txt
    git commit -m "Initial commit" --quiet
}

teardown() {
    # Clean up temp directory
    cd /
    rm -rf "$TEMP_DIR"
}

# =============================================================================
# BASIC COMMAND TESTS
# =============================================================================

@test "coordinate.sh exists and is executable" {
    [ -f "$SCRIPT" ]
    [ -x "$SCRIPT" ]
}

@test "help command shows usage" {
    run "$SCRIPT" help
    [ "$status" -eq 0 ]
    [[ "$output" == *"Usage:"* ]]
    [[ "$output" == *"./coordinate.sh init"* ]]
}

@test "list command shows agents" {
    run "$SCRIPT" list
    [ "$status" -eq 0 ]
    [[ "$output" == *"@product-owner"* ]]
    [[ "$output" == *"@python-coder"* ]]
    [[ "$output" == *"@functional-tester"* ]]
}

@test "list shows all phases" {
    run "$SCRIPT" list
    [ "$status" -eq 0 ]
    [[ "$output" == *"Phase 0: Discovery"* ]]
    [[ "$output" == *"Phase 1: Design"* ]]
    [[ "$output" == *"Phase 2: Tests First"* ]]
    [[ "$output" == *"Phase 3: Development"* ]]
    [[ "$output" == *"Phase 4: Review"* ]]
    [[ "$output" == *"Phase 5: Testing"* ]]
    [[ "$output" == *"Phase 6: Deploy"* ]]
    [[ "$output" == *"Phase 7: Documentation"* ]]
}

@test "workflow command shows TDD info" {
    run "$SCRIPT" workflow
    [ "$status" -eq 0 ]
    [[ "$output" == *"TDD WORKFLOW"* ]]
    [[ "$output" == *"RED"* ]]
    [[ "$output" == *"GREEN"* ]]
}

@test "structure command shows directory layout" {
    run "$SCRIPT" structure
    [ "$status" -eq 0 ]
    [[ "$output" == *"./artifacts/"* ]]
    [[ "$output" == *"python/"* ]]
    [[ "$output" == *"typescript/"* ]]
}

# =============================================================================
# INIT COMMAND TESTS
# =============================================================================

@test "init creates artifacts directory" {
    run "$SCRIPT" init
    [ "$status" -eq 0 ]
    [ -d "./artifacts" ]
}

@test "init creates all required subdirectories" {
    run "$SCRIPT" init
    [ "$status" -eq 0 ]

    # Design phase
    [ -d "./artifacts/database/migrations" ]
    [ -d "./artifacts/api" ]
    [ -d "./artifacts/design/visuals" ]

    # Development phase
    [ -d "./artifacts/python/tests" ]
    [ -d "./artifacts/typescript/tests" ]

    # Testing phase
    [ -d "./artifacts/test-results" ]
    [ -d "./artifacts/ui-test-results/screenshots" ]
    [ -d "./artifacts/security-audit" ]

    # Deploy phase
    [ -d "./artifacts/gcp/terraform" ]

    # Documentation (per doc-standards.md)
    [ -d "./artifacts/context/build" ]
    [ -d "./artifacts/context/specs" ]
    [ -d "./artifacts/context/guides" ]
}

@test "init creates requirements.md template" {
    run "$SCRIPT" init
    [ "$status" -eq 0 ]
    [ -f "./artifacts/requirements.md" ]
}

@test "init is idempotent" {
    # Run init twice
    run "$SCRIPT" init
    [ "$status" -eq 0 ]
    run "$SCRIPT" init
    [ "$status" -eq 0 ]
}

# =============================================================================
# WORKTREE COMMAND TESTS
# =============================================================================

@test "worktree help shows available commands" {
    run "$SCRIPT" worktree help
    [ "$status" -eq 0 ]
    [[ "$output" == *"WORKTREE COMMANDS"* ]]
    [[ "$output" == *"create"* ]]
    [[ "$output" == *"list"* ]]
    [[ "$output" == *"switch"* ]]
}

@test "worktree create requires feature name" {
    run "$SCRIPT" worktree create
    [ "$status" -eq 1 ]
    [[ "$output" == *"Feature name required"* ]]
}

@test "worktree create makes worktrees for all domains" {
    run "$SCRIPT" worktree create test-feature
    [ "$status" -eq 0 ]

    # Check all domain worktrees exist
    [ -d ".worktrees/discovery" ]
    [ -d ".worktrees/design" ]
    [ -d ".worktrees/backend" ]
    [ -d ".worktrees/frontend" ]
    [ -d ".worktrees/review" ]
    [ -d ".worktrees/infra" ]
    [ -d ".worktrees/docs" ]
}

@test "worktree create stores feature name" {
    run "$SCRIPT" worktree create my-feature
    [ "$status" -eq 0 ]
    [ -f ".worktrees/.feature" ]
    [ "$(cat .worktrees/.feature)" = "my-feature" ]
}

@test "worktree create makes correct branch names" {
    "$SCRIPT" worktree create test-feature

    # Check branch exists for each domain
    run git branch --list "feature/test-feature/discovery"
    [[ "$output" == *"feature/test-feature/discovery"* ]]

    run git branch --list "feature/test-feature/backend"
    [[ "$output" == *"feature/test-feature/backend"* ]]
}

@test "worktree list shows all worktrees" {
    "$SCRIPT" worktree create test-feature

    run "$SCRIPT" worktree list
    [ "$status" -eq 0 ]
    [[ "$output" == *"discovery"* ]]
    [[ "$output" == *"backend"* ]]
    [[ "$output" == *"test-feature"* ]]
}

@test "worktree switch requires domain" {
    run "$SCRIPT" worktree switch
    [ "$status" -eq 1 ]
    [[ "$output" == *"Domain required"* ]]
}

@test "worktree switch shows domain agents" {
    "$SCRIPT" worktree create test-feature

    run "$SCRIPT" worktree switch backend
    [ "$status" -eq 0 ]
    [[ "$output" == *"@python-coder"* ]]
    [[ "$output" == *"@functional-tester"* ]]
}

@test "worktree switch shows correct path" {
    "$SCRIPT" worktree create test-feature

    run "$SCRIPT" worktree switch design
    [ "$status" -eq 0 ]
    [[ "$output" == *".worktrees/design"* ]]
}

@test "worktree sync requires domain" {
    run "$SCRIPT" worktree sync
    [ "$status" -eq 1 ]
    [[ "$output" == *"Domain required"* ]]
}

# =============================================================================
# DOMAIN CONSISTENCY TESTS
# =============================================================================

@test "DOMAINS array has 7 elements" {
    # Extract DOMAINS from script
    source <(grep 'DOMAINS=' "$SCRIPT")
    [ "${#DOMAINS[@]}" -eq 7 ]
}

@test "DOMAINS contains all expected values" {
    source <(grep 'DOMAINS=' "$SCRIPT")

    [[ " ${DOMAINS[*]} " == *" discovery "* ]]
    [[ " ${DOMAINS[*]} " == *" design "* ]]
    [[ " ${DOMAINS[*]} " == *" backend "* ]]
    [[ " ${DOMAINS[*]} " == *" frontend "* ]]
    [[ " ${DOMAINS[*]} " == *" review "* ]]
    [[ " ${DOMAINS[*]} " == *" infra "* ]]
    [[ " ${DOMAINS[*]} " == *" docs "* ]]
}

# =============================================================================
# EDGE CASES
# =============================================================================

@test "script handles missing git repo gracefully for worktree" {
    # Create a non-git directory
    mkdir -p /tmp/non-git-test-$$
    cd /tmp/non-git-test-$$

    run "$SCRIPT" worktree create test
    [ "$status" -eq 1 ]
    [[ "$output" == *"Not a git repository"* ]]

    # Cleanup
    cd /
    rm -rf /tmp/non-git-test-$$
}

@test "short aliases work for list" {
    run "$SCRIPT" -l
    [ "$status" -eq 0 ]
    [[ "$output" == *"@product-owner"* ]]
}

@test "worktree alias wt works" {
    run "$SCRIPT" wt help
    [ "$status" -eq 0 ]
    [[ "$output" == *"WORKTREE COMMANDS"* ]]
}

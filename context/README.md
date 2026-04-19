# Context Directory

Portable standards, rules, and agent definitions for multi-agent development workflows.

---

## Quick Reference

| What                       | Where                            | When                                                 |
| -------------------------- | -------------------------------- | ---------------------------------------------------- |
| **Non-negotiable rules**   | `rules/*.mdc`                    | Agent frontmatter lists applicable rules             |
| **Reference docs**         | `standards/*.md`                 | Read when agent needs guidance                       |
| **Agent definitions**      | `agents/*.md`                    | Orchestrator spawns with Task tool                   |
| **Workflows**              | `workflows/*.yaml`               | Defines phase dependencies                           |
| **Framework reference**    | `docs/agentic-framework-reference.md` | Workflows, patterns, personas, adapters, measurement |
| **Output templates**       | `templates/`                     | Handoff, review, artefact formats                    |
| **Writing personas**       | `persona/*.md`                   | Voice/style for human-facing content (blogs, papers) |
| **Validators**             | `scripts/validators/`            | Pre-commit hooks, CI/CD                              |
| **Generators**             | `scripts/generators/`            | CLAUDE.md/AGENTS.md generators                       |

---

## For Agents

**Quick scan** - Read these when spawned:

**Rules** (non-negotiable): [python-env](rules/python-environment.mdc) · [ts-env](rules/typescript-environment.mdc) · [secrets](rules/secrets-management.mdc) · [tdd](rules/tdd-workflow.mdc) · [types](rules/type-safety.mdc) · [outputs](rules/output-locations.mdc) · [commits](rules/git-commits.mdc) · [spelling](rules/british-english.mdc) · [EARS](rules/EARS-notation-requirements.mdc) · [bash](rules/bash-environment.mdc) · [handoff](rules/handoff-hygiene.mdc) · [escalation](rules/escalation.mdc) · [arch-fidelity](rules/architecture-fidelity.mdc) · [ui-reuse](rules/ui-component-reuse.mdc) · [visual](rules/visual-fidelity.mdc) · [quality-gates](rules/quality-gates.mdc) · [browser](rules/browser-automation.mdc)

**Standards** (reference): [coding](standards/coding-standards.md) · [testing](standards/testing-standards.md) · [tech](standards/tech-standards.md) · [doc](standards/doc-standards.md) · [workflow](standards/workflow-standards.md) · [security](standards/security-standards.md) · [context](standards/context-framework.md) · [12-factor](standards/12-factor-principles.md) · [LESS](standards/LESS-Engineering-Principles.md) · [visual](standards/visual-standards.md)

**Workflows**: [build](workflows/build.yaml) · [design](workflows/design.yaml) · [prototype](workflows/prototype.yaml) · [deploy](workflows/deploy.yaml) · [bugfix](workflows/bugfix.yaml) · [full-test](workflows/full-test.yaml) · [content](workflows/content.yaml) · [continuous-improvement](workflows/continuous-improvement.yaml)

**Framework reference**: [agentic-framework-reference](docs/agentic-framework-reference.md)

**Templates**: [index](templates/README.md)

---

## For Humans

### File Type Overview

**Rules** (`rules/*.mdc`):

- Things that **break** if not followed (not style preferences)
- Self-contained, actionable, binary (followed or not)
- Agents load these via frontmatter
- Examples: `uv run pytest` works, bare `pytest` fails; `/secrets/*.json` works, `.env` leaks

**Standards** (`standards/*.md`):

- **How** to do things well (context, rationale, examples)
- Comprehensive reference documentation
- Agents read on-demand (too verbose to preload)
- Examples: Python patterns, TDD philosophy, architecture decisions

**Agents** (`agents/*.md`):

- Specialised agent definitions (who does what)
- Frontmatter lists applicable `rules`, `standards`, and `model`
- `orchestrator.md` defines orchestrator behaviour — read at session start
- Orchestrator spawns with Task tool; see AGENTS.md for the complete registry

**Workflows** (`workflows/*.yaml`):

- Phase definitions, dependencies, quality gates
- Each phase lists agents, outputs, validation
- Source of truth for phase ordering

**Framework reference** (`docs/agentic-framework-reference.md`):

- Default and prototype workflows (phase-by-phase, diagrams)
- Orchestration patterns (single, chain, hive, loop — see `docs/agentic-framework-reference.md`; swarm is vision-level only)
- Writing personas, portability adapters, effectiveness measurement
- Standards, rules, agents, templates, and scripts at operational depth

**Templates** (`templates/`):

- Output formats for artefacts, handoffs, reviews, git, and agent definitions
- The orchestrator selects the appropriate template when constructing a task prompt; agents use whichever template the task prompt specifies
- See `templates/README.md` for the full index

**Personas** (`persona/*.md`):

- Writing voice/style for human-facing content (blogs, papers, marketing)
- NOT for technical handoffs (README, API docs, architecture)
- See `docs/agentic-framework-reference.md` (Writing Personas) for when and how to use them

**Scripts** (`scripts/`):

- `prepare-commit-msg.py` / `.sh`: Git hook — injects token usage from Claude Code session telemetry into Agent-Session commit trailer
- Validators (`validators/`): Pre-commit hooks for rule enforcement (conventional commits, British English, EARS notation, design system, API docs, Supabase boundary, framework docs staleness)
- Generators (`generators/`): Auto-generate CLAUDE.md/AGENTS.md from agent definitions and workflows
- Tests (`tests/`): Validator test suite

### DRY Between Rules & Standards

Some duplication is **intentional**:

- Rules tell agents **what to do** (concise, actionable)
- Standards explain **why and how** (detailed, contextual)

An agent following a rule should succeed without reading standards. Standards exist for when someone asks "why?" or hits an edge case.

---

## Orchestrator Responsibilities

The orchestrator (main Claude session) coordinates work but delegates implementation. Full behaviour defined in `context/agents/orchestrator.md` — read at session start.

**Core rule**: Delegate all implementation to specialised agents. The orchestrator writing code directly silently bypasses the environment rules those agents carry.

**When no agent exists for a task**: create one from `agents/TEMPLATE.md`, then delegate. Do not write implementation directly.

---

## Workflows

See `AGENTS.md` for the workflow index. Full phase definitions in `workflows/*.yaml`.

**build** — Primary development loop: task planning → TDD (red/green/blue) → regression → deployment. Quality gates at tasks-review, coverage, quality-review, final-holistic-review.

**design** — Discovery through design review. Run before `build`. Produces requirements, architecture, API specs, UI designs.

**prototype** — Fast iteration for POCs and experiments. No quality gates. Must rewrite with `build` before production.

**deploy** — GCP cloud deployment. Run after `build` local-deployment phase.

**full-test** — Full regression suite across all modules. Run before merge to master or on demand.

**content** — Human-facing content (blogs, papers, guides) using writing personas.

**bugfix** — Empirical bug reproduction, fix, and verification.

**continuous-improvement** — Framework improvement: reactive (human reports incident) or proactive (review interruptions, incidents, and git log metrics).

**Orchestration patterns**: Single Agent, Sequential Chain, Hive, Iterative Loop (see `docs/agentic-framework-reference.md`; exploration “swarm” is out of scope for shipped YAML — `docs/vision.md`)

---

## Directory Structure

```
context/
├── README.md                      # This file
├── standards/                     # Reference docs (how to do things well)
│   └── *.md                      # coding, testing, tech, doc, workflow, security, 12-factor, LESS, visual
├── rules/                         # Non-negotiables (break if ignored)
│   └── *.mdc                     # python-env, ts-env, secrets, tdd, types, outputs, commits, etc.
├── agents/                        # Agent definitions (who does what)
│   ├── TEMPLATE.md               # Template for new agents
│   ├── orchestrator.md           # Orchestrator behaviour (read at session start)
│   └── *.md                      # Specialised agents (see AGENTS.md for registry)
├── workflows/                     # Workflow patterns (phase dependencies)
│   ├── build.yaml                # Primary TDD development loop
│   ├── design.yaml               # Discovery through design review
│   ├── prototype.yaml            # Fast iteration / POC
│   ├── deploy.yaml               # GCP cloud deployment
│   ├── bugfix.yaml               # Bug reproduction, fix, verification
│   ├── full-test.yaml            # Full regression suite
│   ├── content.yaml              # Human-facing content with personas
│   └── continuous-improvement.yaml # Incident response + retrospective
├── docs/                          # Design essays and operator reference
│   ├── agentic-framework.md            # Why the framework exists (essay)
│   ├── agentic-framework-reference.md # What it contains and how to run it (incl. content workflow)
│   ├── vision.md · journey.md · roadmap.md # New DevX programme documents
├── templates/                     # Output templates (flat — see templates/README.md for index)
├── persona/                       # Writing voice for human-facing content
│   ├── technical-writer.md       # Amara Osei persona (practitioner guides, technical prose)
│   ├── opinionated-blogger.md   # Dr. Sarah Chen persona (blogs, opinion pieces)
│   ├── editor.md                 # Editorial voice
│   └── expert-reviewer.md        # Review voice
├── mcp/                          # MCP server configuration
│   └── mcp.json                  # Template config
└── scripts/                      # Portable tools
    ├── prepare-commit-msg.py    # Hook: inject token metrics into commits
    ├── prepare-commit-msg.sh    # Shell wrapper (symlinked from .git/hooks/)
    ├── validators/               # Rule validators (pre-commit hooks)
    ├── generators/               # CLAUDE.md/AGENTS.md generators
    └── tests/                    # Validator tests
```

---

## Syncing Context Across Projects

**Golden source**: `start-here` repo

Copy the `context/` folder into each project. Use `rsync` or a custom sync script to keep copies current.

---

## Adding New Rules

When something keeps failing because agents don't follow it:

1. **Is it binary?** Can you definitively say "followed" or "not followed"?
2. **Does it break things?** Not just style—actual failures?
3. **Is it actionable?** Can you give clear DO/DON'T commands?

If yes to all three, create a rule in `rules/*.mdc` (keep under 200 tokens).

---

## Adding New Agents

When a task domain needs repeated specialised work:

1. Copy `agents/TEMPLATE.md`
2. Set `name`, `description`, `model` in frontmatter
3. List applicable `rules` and `standards` in frontmatter
4. Write concise body with rules summary and workflow
5. Add to workflow YAML if part of standard process
6. Regenerate AGENTS.md: `uv run python context/scripts/generators/generate_agents_md.py`

---

## See Also

- **AGENTS.md** — auto-generated workflow + agent registry (run `generate_agents_md.py` to update)
- **Root README**: `../README.md` — deployment instructions for context system
- **Standards index**: `standards/README.md` — detailed standards catalogue

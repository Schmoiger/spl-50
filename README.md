# Start Here

Portable multi-agent development context for AI-assisted software engineering.

---

## Quick Deployment

### 1. Copy to Your Project

```bash
# Copy context directory and orchestration guide
cp -r context/ /path/to/your-project/context/
cp CLAUDE.md /path/to/your-project/CLAUDE.md
cp AGENTS.md /path/to/your-project/AGENTS.md
```

### 2. Configure MCP (Optional)

```bash
# Claude Code CLI
cp context/mcp/mcp.json ~/.claude/mcp.json

# Claude Desktop
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
# Windows: %APPDATA%\Claude\claude_desktop_config.json
# Linux: ~/.config/Claude/claude_desktop_config.json

# Cursor IDE
cp context/mcp/mcp.json /path/to/your-project/.mcp.json
```

### 3. Generate CLAUDE.md

```bash
cd /path/to/your-project
uv run python context/scripts/generators/generate_claude_md.py
```

### 4. Create Artefacts Structure

```bash
mkdir -p artefacts/{product,architecture,design,build,test-results,shared}
mkdir -p artefacts/shared/{handoffs,fixtures,mocks}
```

---

## Documentation

- **Getting started**: See `context/README.md` - Complete guide for agents and humans
- **Workflow guide**: See `CLAUDE.md` / `AGENTS.md` - Auto-generated orchestration guide
- **Agent reference**: See `context/agents/` - Individual agent definitions
- **Standards**: See `context/standards/` - Coding, testing, tech stack guidance
- **Workflows**: See `context/workflows/` - Default (TDD) and prototype patterns

---

## Framework Compatibility

This context system works with multiple AI frameworks beyond Claude Code.

**Native support**: Claude Code (CLI), Claude Desktop
**Adaptable to**: LangGraph, CrewAI, AutoGen, Cursor, Aider, Continue, Windsurf

See `context/docs/agentic-framework-reference.md` (Portability and Framework Adapters) for integration guides showing how to load agent definitions, map tools, and adapt workflows for each framework.

---

## Support

- **Issues**: https://github.com/Schmoiger/start-here/issues
- **Full documentation**: `context/README.md`
- **Framework reference**: `context/docs/agentic-framework-reference.md`
- **Customization**: See `context/README.md` for adding agents, rules, validators

---

## What's Included

- **18 specialized agents** - Discovery, design, development, review, testing, deployment
- **14 standards** - Coding, testing, tech stack, documentation, workflows
- **18 rules** - Enforceable constraints with validators
- **9 workflows** in `context/workflows/` - Including build (TDD), design, prototype, content (blogs and papers with personas), deploy, bugfix, full-test, continuous-improvement, retrospective
- **12 templates** - Handoffs, reviews, artefacts

**Total**: ~66 context files for structured, high-quality multi-agent workflows.

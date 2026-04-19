#!/usr/bin/env python3
"""Generate AGENTS.md orchestration guide from context directory.

Creates AGENTS.md: Minimal agent orchestration guide — only what the orchestrator
needs at runtime (phase sequence, agent dispatch, state recovery, spawn pattern).

Usage:
    uv run python context/scripts/generators/generate_agents_md.py [--workflow build]
"""

import argparse
import sys
from pathlib import Path
from typing import Any
import yaml


def load_workflow(workflow_name: str) -> dict[str, Any]:
    """Load workflow YAML file."""
    workflow_path = Path('context/workflows') / f'{workflow_name}.yaml'

    if not workflow_path.exists():
        print(f"❌ Workflow not found: {workflow_path}")
        sys.exit(1)

    with workflow_path.open() as f:
        return yaml.safe_load(f)


def load_all_workflows() -> dict[str, dict]:
    """Load all workflow YAML files, skipping any that fail to parse."""
    workflows: dict[str, dict] = {}
    for wf_file in sorted(Path('context/workflows').glob('*.yaml')):
        try:
            data = yaml.safe_load(wf_file.read_text())
            if data:
                workflows[wf_file.stem] = data
        except yaml.YAMLError as e:
            print(f"⚠️  Skipping {wf_file.name}: {e}")
    return workflows


def collect_all_agents(workflows: dict) -> list[str]:
    """Union of all agents across all workflows, in workflow-stage order."""
    category_order = [
        'product-owner', 'product-expert',
        'solution-architect', 'database-designer', 'api-designer', 'ui-designer', 'visual-designer',
        'functional-tester', 'python-coder', 'typescript-coder',
        'tech-lead', 'code-reviewer', 'principles-reviewer',
        'ui-tester', 'security-tester',
        'devops', 'gcp-devops',
        'documentation',
        'workflow-analyst',
    ]
    all_agents: set[str] = set()
    for data in workflows.values():
        for phase in data.get('phases', []):
            for agent in phase.get('agents', []):
                all_agents.add(agent)
    ordered = [a for a in category_order if a in all_agents]
    remainder = sorted(all_agents - set(ordered))
    return ordered + remainder


def generate_workflow_table(workflows: dict) -> str:
    """Generate workflow index table."""
    rows = [
        "| Workflow | Purpose |",
        "|----------|---------|",
    ]
    for name, data in sorted(workflows.items()):
        desc = _first_sentence(data.get('description', ''))
        rows.append(f"| `{name}` | {desc} |")
    return '\n'.join(rows)


def load_agent_definitions() -> dict[str, dict]:
    """Load all agent definitions."""
    agents = {}
    agents_dir = Path('context/agents')

    for agent_file in agents_dir.glob('*.md'):
        if agent_file.name in ['TEMPLATE.md', 'README.md', 'MODEL-RECOMMENDATIONS.md']:
            continue

        content = agent_file.read_text()

        if not content.startswith('---'):
            continue

        parts = content.split('---', 2)
        if len(parts) < 3:
            continue

        try:
            frontmatter = yaml.safe_load(parts[1])
            agents[frontmatter['name']] = {
                'frontmatter': frontmatter,
                'content': parts[2].strip()
            }
        except (yaml.YAMLError, KeyError):
            continue

    return agents


def extract_description(agent_content: str) -> str:
    """Extract role description from agent content."""
    lines = agent_content.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            return stripped

    return "Agent description not found"


def _first_sentence(text: str) -> str:
    """Return the first sentence of a string (up to first full stop)."""
    idx = text.find('.')
    return text[:idx].strip() if idx != -1 else text.strip()


def _trim_purpose(text: str) -> str:
    """Extract core purpose: first sentence, parentheticals removed."""
    import re
    sentence = _first_sentence(text)
    return re.sub(r'\s*\([^)]*\)', '', sentence).strip()


def generate_phase_sequence(workflow: dict) -> str:
    """Generate single-line phase sequence with gate/parallel markers."""
    parts = []
    for phase in workflow.get('phases', []):
        phase_id = phase['id']
        flags = []
        if phase.get('gate'):
            flags.append('gate')
        if phase.get('parallel'):
            flags.append('parallel')
        flag_str = f" [{','.join(flags)}]" if flags else ''
        parts.append(f"`{phase_id}`{flag_str}")
    return ' → '.join(parts)


def generate_agent_dispatch(workflow: dict, agents: dict) -> str:
    """Generate agent dispatch table for agents used in the workflow."""
    # Collect unique agents in phase order
    seen: set[str] = set()
    used_agents: list[str] = []
    for phase in workflow.get('phases', []):
        for agent_name in phase.get('agents', []):
            if agent_name not in seen:
                seen.add(agent_name)
                used_agents.append(agent_name)
    return _agent_table(used_agents, agents)


def generate_agent_dispatch_all(agent_names: list[str], agents: dict) -> str:
    """Generate agent dispatch table for all agents across all workflows."""
    return _agent_table(agent_names, agents)


def _agent_table(agent_names: list[str], agents: dict) -> str:
    """Render agent dispatch table from an ordered list of agent names."""
    rows = [
        "| Agent | Purpose |",
        "|-------|---------|",
    ]
    for agent_name in agent_names:
        agent_data = agents.get(agent_name, {})
        fm = agent_data.get('frontmatter', {})
        purpose = fm.get('description', '')
        if not purpose and agent_data.get('content'):
            purpose = extract_description(agent_data['content'])
        purpose = _trim_purpose(purpose)
        rows.append(f"| `@{agent_name}` | {purpose} |")
    return '\n'.join(rows)


def generate_state_recovery_files(workflow: dict) -> str:
    """Generate concise state recovery file list."""
    state_recovery = workflow.get('state_recovery', {})
    critical_files = state_recovery.get('critical_files', [])
    if not critical_files:
        return "_No state recovery files defined._"
    return '\n'.join(f"- `{f}`" for f in critical_files)


# ---------------------------------------------------------------------------
# Legacy functions — kept for backwards compatibility with tests
# ---------------------------------------------------------------------------

def generate_workflow_diagram(workflow: dict) -> str:
    """Generate Mermaid diagram from workflow phases."""
    lines = ["```mermaid", "flowchart TD"]
    phases = workflow.get('phases', [])

    for i, phase in enumerate(phases):
        phase_id = phase['id']
        phase_name = phase.get('name', phase_id)
        agents = phase.get('agents', [])

        lines.append(f'    subgraph {phase_id}["{phase_name}"]')
        for agent in agents:
            agent_id = f"{phase_id}_{agent.replace('-', '_')}"
            lines.append(f'        {agent_id}["@{agent}"]')
        lines.append('    end')

        if 'depends_on' in phase:
            for dep in phase['depends_on']:
                lines.append(f'    {dep} --> {phase_id}')
        elif i > 0:
            prev_phase_id = phases[i - 1]['id']
            lines.append(f'    {prev_phase_id} --> {phase_id}')

        if phase.get('gate'):
            lines.append(f'    {phase_id}:::gateStyle')

    lines.append('    classDef gateStyle fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px')
    lines.append("```")
    return '\n'.join(lines)


def generate_phase_table(workflow: dict, agents: dict) -> str:
    """Generate compact numbered phase list."""
    items = []
    for i, phase in enumerate(workflow.get('phases', []), 1):
        phase_id = phase['id']
        phase_name = phase.get('name', phase_id)
        phase_agents = phase.get('agents', [])

        flags = []
        if phase.get('gate'):
            flags.append('gate')
        if phase.get('parallel'):
            flags.append('parallel')
        if phase.get('optional'):
            flags.append('optional')

        flag_str = (' `[' + ' · '.join(flags) + ']`') if flags else ''
        agent_str = ' · '.join(f'@{a}' for a in phase_agents)

        lines = [f"{i}. **{phase_id}** — {phase_name}{flag_str}"]
        if agent_str:
            lines.append(f"   {agent_str}")

        skills = phase.get('skills', [])
        if skills:
            skill_str = ' · '.join(f'`{s}`' for s in skills)
            lines.append(f"   Skills: {skill_str}")

        items.append('\n'.join(lines))

    return '\n\n'.join(items)


def generate_phase_details(workflow: dict, agents: dict) -> str:
    """Generate detailed phase descriptions."""
    sections = []
    for phase in workflow.get('phases', []):
        phase_id = phase['id']
        phase_name = phase.get('name', phase_id)
        phase_agents = phase.get('agents', [])

        section = [f"#### {phase_name}"]
        section.append(f"**Phase ID**: `{phase_id}`")

        if 'depends_on' in phase:
            deps = ', '.join(f"`{d}`" for d in phase['depends_on'])
            section.append(f"**Depends On**: {deps}")

        if phase.get('parallel'):
            section.append("**Execution**: Parallel (agents run simultaneously)")
        if phase.get('sequential'):
            section.append("**Execution**: Sequential (agents run in order)")
        if phase.get('optional'):
            section.append("**Optional**: Can be skipped")
        if phase.get('gate'):
            section.append("**Quality Gate**: ⚠️ Approval required before proceeding")

        section.append("\n**Agents:**")
        for agent_name in phase_agents:
            if agent_name in agents:
                section.append(f"- `@{agent_name}` - See `context/agents/{agent_name}.md`")
            else:
                section.append(f"- `@{agent_name}`")

        if 'outputs' in phase:
            section.append("\n**Outputs:**")
            for output in phase['outputs']:
                section.append(f"- {output}")
        if 'validation' in phase:
            section.append("\n**Validation:**")
            for validation in phase['validation']:
                section.append(f"- {validation}")
        if 'notes' in phase:
            section.append("\n**Notes:**")
            for note in phase['notes']:
                section.append(f"- {note}")

        sections.append('\n'.join(section))

    return '\n\n'.join(sections)


def generate_agent_reference(agents: dict) -> str:
    """Generate agent reference section grouped by category."""
    sections = []
    categories = {
        'Discovery': ['product-owner', 'product-expert'],
        'Design': ['solution-architect', 'database-designer', 'api-designer', 'ui-designer', 'visual-designer'],
        'Development': ['functional-tester', 'python-coder', 'typescript-coder'],
        'Review': ['tech-lead', 'code-reviewer', 'principles-reviewer'],
        'Testing': ['ui-tester', 'security-tester'],
        'Deployment': ['gcp-devops', 'devops'],
        'Documentation': ['documentation'],
        'Analysis': ['workflow-analyst'],
    }
    for category, agent_names in categories.items():
        present = [a for a in agent_names if a in agents]
        if not present:
            continue
        lines = [f"### {category}"]
        for agent_name in present:
            lines.append(f"- **@{agent_name}** — `context/agents/{agent_name}.md`")
        sections.append('\n'.join(lines))
    return '\n\n'.join(sections)


def generate_quality_gates(workflow: dict) -> str:
    """Generate quality gates section."""
    gates = workflow.get('quality_gates', [])
    if not gates:
        return "No quality gates defined for this workflow."

    sections = []
    for gate in gates:
        phase = gate.get('phase', 'unknown')
        gate_type = gate.get('type', 'unknown')
        desc = gate.get('description', '')
        required = gate.get('required', False)

        section = [f"#### {phase.replace('-', ' ').title()}"]
        section.append(f"**Type**: {gate_type}")
        section.append(f"**Required**: {'Yes' if required else 'No'}")
        section.append(f"\n{desc}")

        if 'criteria' in gate:
            section.append("\n**Criteria:**")
            for criterion in gate['criteria']:
                metric = criterion.get('metric')
                threshold = criterion.get('threshold')
                operator = criterion.get('operator')
                section.append(f"- {metric} {operator} {threshold}")

        sections.append('\n'.join(section))

    return '\n\n'.join(sections) if sections else "No quality gates defined."


def generate_workflow_rules(workflow: dict) -> str:
    """Generate workflow rules section."""
    rules = workflow.get('workflow_rules', [])
    warnings = workflow.get('warnings', [])
    sections = []

    if rules:
        for rule in rules:
            sections.append(f"- {rule}")
    if warnings:
        sections.append("\n### Warnings\n")
        for warning in warnings:
            sections.append(f"{warning}")

    return '\n'.join(sections) if sections else "No specific workflow rules defined."


def generate_state_recovery(workflow: dict) -> str:
    """Generate state recovery section (verbose form)."""
    state_recovery = workflow.get('state_recovery', {})
    if not state_recovery:
        return ""

    sections = ["## State Recovery After Context Compaction\n"]
    sections.append("After compaction, read these files before resuming:\n")

    for step in state_recovery.get('after_compaction', []):
        sections.append(f"- [ ] {step}")

    critical_files = state_recovery.get('critical_files', [])
    if critical_files:
        sections.append("\n**Critical state files:**")
        for file in critical_files:
            sections.append(f"- `{file}`")

    return '\n'.join(sections)


def generate_estimation_guidance(workflow: dict) -> str:
    """Generate effort estimation guidance section."""
    estimation = workflow.get('estimation_guidance', [])
    if not estimation:
        return ""
    sections = ["## Effort Estimation Guidance\n",
                "**IMPORTANT**: Estimate effort in tokens, NOT time.\n"]
    for guideline in estimation:
        sections.append(f"- {guideline}")
    return '\n'.join(sections)


def generate_parallel_planning(workflow: dict) -> str:
    """Generate parallel planning guidance section."""
    parallel = workflow.get('parallel_planning', [])
    if not parallel:
        return ""
    return '\n'.join(f"- {g}" for g in parallel)


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_agents_md(workflow_name: str) -> str:
    """Generate minimal AGENTS.md — only what the orchestrator needs at runtime."""
    agents = load_agent_definitions()
    all_workflows = load_all_workflows()
    all_agent_names = collect_all_agents(all_workflows)

    return f"""# Agents

## On Start
Glob `**/artefacts/README.md` and read all matches. Run `git log --oneline -5`.
Read `context/agents/orchestrator.md`.
Read `artefacts/build/HANDOFF.md` if it exists — the `Workflow:` field identifies the active workflow.
Load `context/workflows/<workflow>.yaml`. If no HANDOFF.md exists, ask the user which workflow to start.

## Workflows

{generate_workflow_table(all_workflows)}

## Agents

{generate_agent_dispatch_all(all_agent_names, agents)}

**Spawn**: `"Read context/agents/{{name}}.md before starting. [task]"`

_Auto-generated by context/scripts/generators/generate_agents_md.py — do not edit manually_
"""


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate AGENTS.md from context directory'
    )
    parser.add_argument(
        '--workflow',
        default='build',
        help='Workflow to use (default: build). Available: build, prototype, design, deploy, full-test'
    )

    args = parser.parse_args()
    print(f"🔧 Generating AGENTS.md from {args.workflow} workflow...")

    try:
        content = generate_agents_md(args.workflow)
        agents_path = Path('AGENTS.md')
        agents_path.write_text(content)
        print(f"✅ Generated AGENTS.md ({len(content)} bytes)")
        print(f"   Workflow: {args.workflow}")
        print(f"   Location: {agents_path.absolute()}")

    except Exception as e:
        print(f"❌ Error generating files: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

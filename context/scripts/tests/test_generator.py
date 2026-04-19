"""Tests for AGENTS.md generator."""

import pytest
from pathlib import Path
import sys
import yaml

# Add generators directory to path so we can import generator
sys.path.insert(0, str(Path(__file__).parent.parent / 'generators'))

import generate_agents_md as gen
load_workflow = gen.load_workflow
load_agent_definitions = gen.load_agent_definitions
extract_description = gen.extract_description
generate_workflow_diagram = gen.generate_workflow_diagram
generate_phase_details = gen.generate_phase_details
generate_phase_sequence = gen.generate_phase_sequence
generate_phase_table = gen.generate_phase_table
generate_agent_dispatch = gen.generate_agent_dispatch
generate_agent_reference = gen.generate_agent_reference
generate_quality_gates = gen.generate_quality_gates
generate_workflow_rules = gen.generate_workflow_rules
generate_state_recovery_files = gen.generate_state_recovery_files
generate_agents_md = gen.generate_agents_md


class TestWorkflowLoading:
    """Tests for workflow loading."""

    def test_load_workflow(self, test_workflow, monkeypatch):
        """Test loading workflow from YAML file."""
        workflow = yaml.safe_load(test_workflow.read_text())
        assert workflow['name'] == 'test-workflow'
        assert 'phases' in workflow
        assert len(workflow['phases']) == 2

    def test_workflow_has_phases(self, test_workflow):
        """Test that workflow contains phases."""
        workflow = yaml.safe_load(test_workflow.read_text())
        assert 'phases' in workflow
        phases = workflow['phases']
        assert len(phases) > 0
        assert 'id' in phases[0]
        assert 'name' in phases[0]
        assert 'agents' in phases[0]


class TestAgentLoading:
    """Tests for agent definition loading."""

    def test_extract_description(self):
        """Test extracting description from agent content."""
        content = """## Role

This is a test agent for validation purposes.

## Workflow

1. Do something
"""
        desc = extract_description(content)
        assert desc == "This is a test agent for validation purposes."

    def test_extract_description_skips_headers(self):
        """Test that description extraction skips headers."""
        content = """## Role

## Another Header

This is the description.
"""
        desc = extract_description(content)
        assert desc == "This is the description."

    def test_extract_description_missing(self):
        """Test fallback when no description found."""
        content = """## Role

"""
        desc = extract_description(content)
        assert "not found" in desc.lower()


class TestDiagramGeneration:
    """Tests for workflow diagram generation."""

    def test_generate_workflow_diagram(self, test_workflow):
        """Test generating Mermaid diagram from workflow."""
        workflow = yaml.safe_load(test_workflow.read_text())
        diagram = generate_workflow_diagram(workflow)

        assert diagram.startswith("```mermaid")
        assert diagram.endswith("```")
        assert "flowchart TD" in diagram
        assert "subgraph" in diagram
        assert "phase1" in diagram
        assert "phase2" in diagram

    def test_diagram_includes_dependencies(self, test_workflow):
        """Test that diagram includes phase dependencies."""
        workflow = yaml.safe_load(test_workflow.read_text())
        diagram = generate_workflow_diagram(workflow)

        # phase2 depends on phase1
        assert "phase1 --> phase2" in diagram

    def test_diagram_marks_gates(self, test_workflow):
        """Test that diagram marks quality gates."""
        workflow = yaml.safe_load(test_workflow.read_text())
        diagram = generate_workflow_diagram(workflow)

        # phase2 is marked as gate
        assert "gateStyle" in diagram


class TestPhaseTable:
    """Tests for compact phase table generation."""

    def test_generate_phase_table(self, test_workflow):
        """Test generating compact phase list."""
        workflow = yaml.safe_load(test_workflow.read_text())
        agents = {
            'test-agent': {'frontmatter': {'name': 'test-agent'}, 'content': 'Test agent'},
            'another-agent': {'frontmatter': {'name': 'another-agent'}, 'content': 'Another agent'},
        }

        table = generate_phase_table(workflow, agents)

        assert "phase1" in table
        assert "phase2" in table
        assert "@test-agent" in table
        assert "@another-agent" in table

    def test_phase_table_marks_gates(self, test_workflow):
        """Test that phase table marks quality gates."""
        workflow = yaml.safe_load(test_workflow.read_text())
        table = generate_phase_table(workflow, {})

        assert "gate" in table

    def test_phase_table_marks_parallel(self):
        """Test that phase table marks parallel phases."""
        workflow = {
            'phases': [
                {'id': 'p1', 'name': 'Phase One', 'agents': ['agent-a', 'agent-b'], 'parallel': True}
            ]
        }
        table = generate_phase_table(workflow, {})

        assert "parallel" in table

    def test_phase_table_shows_skills(self):
        """Test that phase table shows skills when present."""
        workflow = {
            'phases': [
                {
                    'id': 'p1',
                    'name': 'Phase One',
                    'agents': ['agent-a'],
                    'skills': ['superpowers:test-driven-development']
                }
            ]
        }
        table = generate_phase_table(workflow, {})

        assert "superpowers:test-driven-development" in table


class TestPhaseDetails:
    """Tests for verbose phase details generation (backwards compatibility)."""

    def test_generate_phase_details(self, test_workflow):
        """Test generating detailed phase descriptions."""
        workflow = yaml.safe_load(test_workflow.read_text())
        agents = {
            'test-agent': {'frontmatter': {'name': 'test-agent'}, 'content': 'Test agent'},
            'another-agent': {'frontmatter': {'name': 'another-agent'}, 'content': 'Another test agent'},
        }

        details = generate_phase_details(workflow, agents)

        assert "Phase One" in details
        assert "Phase Two" in details
        assert "phase1" in details
        assert "phase2" in details
        assert "@test-agent" in details
        assert "@another-agent" in details

    def test_phase_details_includes_dependencies(self, test_workflow):
        """Test that phase details show dependencies."""
        workflow = yaml.safe_load(test_workflow.read_text())
        details = generate_phase_details(workflow, {})

        assert "Depends On" in details
        assert "`phase1`" in details

    def test_phase_details_marks_gates(self, test_workflow):
        """Test that phase details mark quality gates."""
        workflow = yaml.safe_load(test_workflow.read_text())
        details = generate_phase_details(workflow, {})

        assert "Quality Gate" in details


class TestAgentReference:
    """Tests for agent reference generation."""

    def test_generate_agent_reference(self):
        """Test generating agent reference section."""
        agents = {
            'product-owner': {
                'frontmatter': {'name': 'product-owner'},
                'content': 'Defines requirements and user stories'
            },
            'python-coder': {
                'frontmatter': {'name': 'python-coder'},
                'content': 'Writes production Python code'
            }
        }

        reference = generate_agent_reference(agents)

        assert "Discovery" in reference
        assert "Development" in reference
        assert "@product-owner" in reference
        assert "@python-coder" in reference
        assert "context/agents/product-owner.md" in reference
        assert "context/agents/python-coder.md" in reference

    def test_generate_agent_reference_skips_missing(self):
        """Test that only present agents are included."""
        agents = {
            'python-coder': {
                'frontmatter': {'name': 'python-coder'},
                'content': 'Writes production Python code'
            }
        }

        reference = generate_agent_reference(agents)

        assert "@python-coder" in reference
        # product-owner not present, Discovery section should be absent
        assert "@product-owner" not in reference


class TestQualityGates:
    """Tests for quality gates generation."""

    def test_generate_quality_gates(self, test_workflow):
        """Test generating quality gates section."""
        workflow = yaml.safe_load(test_workflow.read_text())
        gates_section = generate_quality_gates(workflow)

        assert "Phase2" in gates_section or "phase2" in gates_section
        assert "approval" in gates_section
        assert "Yes" in gates_section

    def test_quality_gates_with_criteria(self):
        """Test quality gates with criteria."""
        workflow = {
            'quality_gates': [
                {
                    'phase': 'verification',
                    'type': 'metrics',
                    'required': True,
                    'description': 'Coverage check',
                    'criteria': [
                        {
                            'metric': 'test_coverage',
                            'threshold': 90,
                            'operator': '>='
                        }
                    ]
                }
            ]
        }

        gates_section = generate_quality_gates(workflow)

        assert "Criteria" in gates_section
        assert "test_coverage" in gates_section
        assert ">= 90" in gates_section

    def test_no_quality_gates(self):
        """Test handling of workflow with no quality gates."""
        workflow = {'quality_gates': []}
        gates_section = generate_quality_gates(workflow)

        assert "No quality gates" in gates_section


class TestWorkflowRules:
    """Tests for workflow rules generation."""

    def test_generate_workflow_rules(self, test_workflow):
        """Test generating workflow rules section."""
        workflow = yaml.safe_load(test_workflow.read_text())
        rules_section = generate_workflow_rules(workflow)

        assert "Rule 1" in rules_section
        assert "Rule 2" in rules_section

    def test_workflow_warnings(self, test_workflow):
        """Test that warnings are included."""
        workflow = yaml.safe_load(test_workflow.read_text())
        rules_section = generate_workflow_rules(workflow)

        assert "⚠️" in rules_section
        assert "Test warning" in rules_section

    def test_no_rules_or_warnings(self):
        """Test handling of workflow with no rules."""
        workflow = {}
        rules_section = generate_workflow_rules(workflow)

        assert "No specific workflow" in rules_section


class TestPhaseSequence:
    """Tests for single-line phase sequence generation."""

    def test_generate_phase_sequence(self, test_workflow):
        """Test that phase sequence is a single line with all phase IDs."""
        workflow = yaml.safe_load(test_workflow.read_text())
        seq = generate_phase_sequence(workflow)

        assert "phase1" in seq
        assert "phase2" in seq
        assert "→" in seq

    def test_phase_sequence_marks_gates(self, test_workflow):
        """Test that gate phases are marked in the sequence."""
        workflow = yaml.safe_load(test_workflow.read_text())
        seq = generate_phase_sequence(workflow)

        assert "gate" in seq

    def test_phase_sequence_marks_parallel(self):
        """Test that parallel phases are marked in the sequence."""
        workflow = {
            'phases': [
                {'id': 'p1', 'name': 'Phase One', 'agents': [], 'parallel': True}
            ]
        }
        seq = generate_phase_sequence(workflow)

        assert "parallel" in seq

    def test_phase_sequence_is_single_line(self, test_workflow):
        """Test that the sequence contains no newlines."""
        workflow = yaml.safe_load(test_workflow.read_text())
        seq = generate_phase_sequence(workflow)

        assert '\n' not in seq


class TestAgentDispatch:
    """Tests for agent dispatch table generation."""

    def test_generate_agent_dispatch(self, test_workflow):
        """Test that dispatch table includes agents from workflow phases."""
        workflow = yaml.safe_load(test_workflow.read_text())
        agents = {
            'test-agent': {
                'frontmatter': {'name': 'test-agent', 'description': 'Runs tests for the project.'},
                'content': 'You are a tester.'
            },
            'another-agent': {
                'frontmatter': {'name': 'another-agent', 'description': 'Reviews code quality.'},
                'content': 'You are a reviewer.'
            },
        }

        table = generate_agent_dispatch(workflow, agents)

        assert "@test-agent" in table
        assert "@another-agent" in table
        assert "context/agents/" not in table

    def test_agent_dispatch_uses_first_sentence(self, test_workflow):
        """Test that long descriptions are truncated to first sentence."""
        workflow = yaml.safe_load(test_workflow.read_text())
        agents = {
            'test-agent': {
                'frontmatter': {
                    'name': 'test-agent',
                    'description': 'Runs tests. Also does other things after the first sentence.'
                },
                'content': ''
            },
        }

        table = generate_agent_dispatch(workflow, agents)

        assert "Runs tests" in table
        assert "Also does other things" not in table

    def test_agent_dispatch_falls_back_to_body(self, test_workflow):
        """Test fallback to body content when no frontmatter description."""
        workflow = yaml.safe_load(test_workflow.read_text())
        agents = {
            'test-agent': {
                'frontmatter': {'name': 'test-agent'},
                'content': 'Writes failing tests for all acceptance criteria.'
            },
        }

        table = generate_agent_dispatch(workflow, agents)

        assert "Writes failing tests" in table

    def test_agent_dispatch_only_includes_workflow_agents(self):
        """Test that only agents used in the workflow are included."""
        workflow = {
            'phases': [
                {'id': 'p1', 'name': 'Phase One', 'agents': ['agent-a']}
            ]
        }
        agents = {
            'agent-a': {'frontmatter': {'name': 'agent-a', 'description': 'Does A.'}, 'content': ''},
            'agent-b': {'frontmatter': {'name': 'agent-b', 'description': 'Does B.'}, 'content': ''},
        }

        table = generate_agent_dispatch(workflow, agents)

        assert "@agent-a" in table
        assert "@agent-b" not in table


class TestStateRecoveryFiles:
    """Tests for state recovery file list generation."""

    def test_generate_state_recovery_files(self):
        """Test that critical files are listed."""
        workflow = {
            'state_recovery': {
                'critical_files': ['artefacts/tasks.md', '{service}/HANDOFF.md']
            }
        }
        result = generate_state_recovery_files(workflow)

        assert "artefacts/tasks.md" in result
        assert "{service}/HANDOFF.md" in result

    def test_state_recovery_files_empty(self):
        """Test fallback when no critical files defined."""
        result = generate_state_recovery_files({})

        assert result  # non-empty fallback message


class TestFullGeneration:
    """Tests for complete AGENTS.md generation."""

    def _mock(self, monkeypatch, test_workflow):
        def mock_load_workflow(workflow_name):
            return yaml.safe_load(test_workflow.read_text())

        def mock_load_agents():
            return {
                'test-agent': {
                    'frontmatter': {'name': 'test-agent', 'description': 'Runs tests.'},
                    'content': 'You are a tester.'
                },
                'another-agent': {
                    'frontmatter': {'name': 'another-agent', 'description': 'Reviews code.'},
                    'content': 'You are a reviewer.'
                },
            }

        monkeypatch.setattr('generate_agents_md.load_workflow', mock_load_workflow)
        monkeypatch.setattr('generate_agents_md.load_agent_definitions', mock_load_agents)

    def test_generate_agents_md_structure(self, test_workflow, monkeypatch):
        """Test that generated AGENTS.md has the minimal required sections."""
        self._mock(monkeypatch, test_workflow)
        content = generate_agents_md('test-workflow')

        assert "# Multi-Agent Orchestration Guide" in content
        assert "## Agents" in content
        assert "Spawning" in content

    def test_generated_md_includes_workflow_name(self, test_workflow, monkeypatch):
        """Test that workflow name is included in output."""
        self._mock(monkeypatch, test_workflow)
        content = generate_agents_md('test-workflow')

        assert "test-workflow" in content

    def test_generated_md_portable_paths(self, test_workflow, monkeypatch):
        """Test that generated markdown uses portable paths."""
        self._mock(monkeypatch, test_workflow)
        content = generate_agents_md('test-workflow')

        assert "context/" in content
        assert "/Users/" not in content
        assert "/home/" not in content

    def test_generated_md_includes_phases(self, test_workflow, monkeypatch):
        """Test that workflow agents appear (phases visible via dispatch table)."""
        self._mock(monkeypatch, test_workflow)
        content = generate_agents_md('test-workflow')

        assert "@test-agent" in content
        assert "@another-agent" in content

    def test_generated_md_includes_agents(self, test_workflow, monkeypatch):
        """Test that workflow agents appear in the dispatch table."""
        self._mock(monkeypatch, test_workflow)
        content = generate_agents_md('test-workflow')

        assert "@test-agent" in content
        assert "@another-agent" in content

"""
Main CLI application for the spec-driven agent workflow system.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..core import SpecDrivenContextEngine, SpecDrivenWorkflowOrchestrator
from ..models.project import Project, ProjectStatus

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def app():
    """
    Spec-Driven Agent Workflow CLI

    A comprehensive spec-driven development workflow that combines the best practices
    from BMAD-METHOD, Context Engineering, and Spec-Driven Development, enhanced with
    A2A (Agent-to-Agent) communication protocols.
    """
    pass


@app.command()
@click.option("--name", required=True, help="Project name")
@click.option("--description", required=True, help="Project description")
@click.option(
    "--slug", help="URL-friendly project identifier (auto-generated if not provided)"
)
@click.option(
    "--output", "-o", type=click.Path(), help="Output directory for project files"
)
def create(name: str, description: str, slug: Optional[str], output: Optional[str]):
    """Create a new spec-driven project."""

    if not slug:
        slug = name.lower().replace(" ", "-").replace("_", "-")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating project...", total=None)

        try:
            # Create project
            project = Project(
                name=name,
                slug=slug,
                description=description,
                status=ProjectStatus.DRAFT,
            )

            # Initialize context engine
            context_engine = SpecDrivenContextEngine()

            # Create context
            context = asyncio.run(context_engine.create_context(project))

            # Initialize workflow orchestrator
            workflow_orchestrator = SpecDrivenWorkflowOrchestrator()

            # Start workflow
            workflow = asyncio.run(workflow_orchestrator.start_workflow(project))

            progress.update(task, description="Project created successfully!")

            # Display project info
            display_project_info(project, context, workflow)

            # Save project files if output directory specified
            if output:
                save_project_files(project, context, workflow, Path(output))

        except Exception as e:
            console.print(f"[red]Error creating project: {e}[/red]")
            sys.exit(1)


@app.command()
@click.argument("project_id")
@click.option(
    "--from-file", type=click.Path(exists=True), help="Requirements file path"
)
@click.option(
    "--interactive", "-i", is_flag=True, help="Interactive requirements gathering"
)
def spec(project_id: str, from_file: Optional[str], interactive: bool):
    """Generate specifications for a project."""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating specifications...", total=None)

        try:
            if from_file:
                progress.update(task, description="Reading requirements file...")
                requirements = read_requirements_file(from_file)

                progress.update(task, description="Analyzing requirements...")
                # This would call the Analyst Agent
                analysis = analyze_requirements(requirements)

                progress.update(task, description="Generating specifications...")
                # This would call the Architect Agent
                specs = generate_specifications(analysis)

            elif interactive:
                progress.update(task, description="Starting interactive session...")
                # This would start an interactive session with the Analyst Agent
                specs = interactive_requirements_gathering(project_id)

            else:
                console.print(
                    "[yellow]Please specify either --from-file or "
                    "--interactive[/yellow]"
                )
                return

            progress.update(task, description="Specifications generated successfully!")

            # Display specifications
            display_specifications(specs)

        except Exception as e:
            console.print(f"[red]Error generating specifications: {e}[/red]")
            sys.exit(1)


@app.command()
@click.argument("project_id")
@click.option("--api-spec", is_flag=True, help="Generate API specifications")
@click.option("--architecture", is_flag=True, help="Generate architecture design")
@click.option("--full", is_flag=True, help="Generate complete design")
def architect(project_id: str, api_spec: bool, architecture: bool, full: bool):
    """Design architecture and generate specifications."""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Designing architecture...", total=None)

        try:
            if full or api_spec:
                progress.update(task, description="Generating API specifications...")
                # This would call the Architect Agent
                api_specs = generate_api_specifications(project_id)

            if full or architecture:
                progress.update(task, description="Designing system architecture...")
                # This would call the Architect Agent
                arch_design = design_architecture(project_id)

            progress.update(task, description="Architecture design completed!")

            # Display results
            if full or api_spec:
                display_api_specifications(api_specs)

            if full or architecture:
                display_architecture(arch_design)

        except Exception as e:
            console.print(f"[red]Error designing architecture: {e}[/red]")
            sys.exit(1)


@app.command()
@click.argument("project_id")
@click.option("--story", help="Specific user story to implement")
@click.option("--module", help="Specific module to implement")
@click.option("--all", is_flag=True, help="Implement all pending stories")
def developer(project_id: str, story: Optional[str], module: Optional[str], all: bool):
    """Implement features and generate code."""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Implementing features...", total=None)

        try:
            if story:
                progress.update(task, description=f"Implementing story: {story}...")
                # This would call the Developer Agent
                implementation = implement_story(project_id, story)

            elif module:
                progress.update(task, description=f"Implementing module: {module}...")
                # This would call the Developer Agent
                implementation = implement_module(project_id, module)

            elif all:
                progress.update(task, description="Implementing all pending stories...")
                # This would call the Developer Agent
                implementation = implement_all_stories(project_id)

            else:
                console.print(
                    "[yellow]Please specify --story, --module, or --all[/yellow]"
                )
                return

            progress.update(task, description="Implementation completed!")

            # Display implementation results
            display_implementation(implementation)

        except Exception as e:
            console.print(f"[red]Error implementing features: {e}[/red]")
            sys.exit(1)


@app.command()
@click.argument("project_id")
@click.option("--module", help="Specific module to test")
@click.option("--integration", is_flag=True, help="Run integration tests")
@click.option("--e2e", is_flag=True, help="Run end-to-end tests")
@click.option("--all", is_flag=True, help="Run all tests")
def qa(project_id: str, module: Optional[str], integration: bool, e2e: bool, all: bool):
    """Run tests and validate implementation."""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running tests...", total=None)

        try:
            if module:
                progress.update(task, description=f"Testing module: {module}...")
                # This would call the QA Agent
                test_results = test_module(project_id, module)

            elif integration:
                progress.update(task, description="Running integration tests...")
                # This would call the QA Agent
                test_results = run_integration_tests(project_id)

            elif e2e:
                progress.update(task, description="Running end-to-end tests...")
                # This would call the QA Agent
                test_results = run_e2e_tests(project_id)

            elif all:
                progress.update(task, description="Running all tests...")
                # This would call the QA Agent
                test_results = run_all_tests(project_id)

            else:
                console.print(
                    "[yellow]Please specify --module, --integration, --e2e, "
                    "or --all[/yellow]"
                )
                return

            progress.update(task, description="Testing completed!")

            # Display test results
            display_test_results(test_results)

        except Exception as e:
            console.print(f"[red]Error running tests: {e}[/red]")
            sys.exit(1)


@app.command()
@click.argument("project_id")
def status(project_id: str):
    """Show project status and workflow progress."""

    try:
        # Get project status
        project_status = get_project_status(project_id)

        # Display status
        display_project_status(project_status)

    except Exception as e:
        console.print(f"[red]Error getting project status: {e}[/red]")
        sys.exit(1)


# Helper functions (placeholders for now)
def display_project_info(project: Project, context, workflow):
    """Display project information."""
    table = Table(title=f"Project: {project.name}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Name", project.name)
    table.add_row("Slug", project.slug)
    table.add_row("Description", project.description)
    table.add_row("Status", project.status)
    table.add_row("Context ID", str(context.id))
    table.add_row("Workflow ID", str(workflow.id))

    console.print(table)


def save_project_files(project: Project, context, workflow, output_dir: Path):
    """Save project files to output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save project configuration
    project_file = output_dir / "project.json"
    with open(project_file, "w") as f:
        json.dump(project.model_dump(), f, indent=2, default=str)

    # Save context
    context_file = output_dir / "context.json"
    with open(context_file, "w") as f:
        json.dump(context.model_dump(), f, indent=2, default=str)

    # Save workflow
    workflow_file = output_dir / "workflow.json"
    with open(workflow_file, "w") as f:
        json.dump(workflow.model_dump(), f, indent=2, default=str)

    console.print(f"[green]Project files saved to: {output_dir}[/green]")


def read_requirements_file(file_path: str):
    """Read requirements from file."""
    # Placeholder implementation
    return {"requirements": "Read from file"}


def analyze_requirements(requirements):
    """Analyze requirements using Analyst Agent."""
    # Placeholder implementation
    return {"analysis": "Requirements analyzed"}


def generate_specifications(analysis):
    """Generate specifications using Architect Agent."""
    # Placeholder implementation
    return {"specifications": "Generated from analysis"}


def interactive_requirements_gathering(project_id: str):
    """Interactive requirements gathering with Analyst Agent."""
    # Placeholder implementation
    return {"specifications": "Gathered interactively"}


def display_specifications(specs):
    """Display specifications."""
    console.print("[green]Specifications generated successfully![/green]")
    console.print(json.dumps(specs, indent=2))


def generate_api_specifications(project_id: str):
    """Generate API specifications using Architect Agent."""
    # Placeholder implementation
    return {"api_specs": "Generated API specifications"}


def design_architecture(project_id: str):
    """Design system architecture using Architect Agent."""
    # Placeholder implementation
    return {"architecture": "Designed system architecture"}


def display_api_specifications(api_specs):
    """Display API specifications."""
    console.print("[green]API specifications generated![/green]")
    console.print(json.dumps(api_specs, indent=2))


def display_architecture(arch_design):
    """Display architecture design."""
    console.print("[green]Architecture design completed![/green]")
    console.print(json.dumps(arch_design, indent=2))


def implement_story(project_id: str, story: str):
    """Implement user story using Developer Agent."""
    # Placeholder implementation
    return {"implementation": f"Implemented story: {story}"}


def implement_module(project_id: str, module: str):
    """Implement module using Developer Agent."""
    # Placeholder implementation
    return {"implementation": f"Implemented module: {module}"}


def implement_all_stories(project_id: str):
    """Implement all pending stories using Developer Agent."""
    # Placeholder implementation
    return {"implementation": "Implemented all stories"}


def display_implementation(implementation):
    """Display implementation results."""
    console.print("[green]Implementation completed![/green]")
    console.print(json.dumps(implementation, indent=2))


def test_module(project_id: str, module: str):
    """Test module using QA Agent."""
    # Placeholder implementation
    return {"test_results": f"Tested module: {module}"}


def run_integration_tests(project_id: str):
    """Run integration tests using QA Agent."""
    # Placeholder implementation
    return {"test_results": "Integration tests completed"}


def run_e2e_tests(project_id: str):
    """Run end-to-end tests using QA Agent."""
    # Placeholder implementation
    return {"test_results": "E2E tests completed"}


def run_all_tests(project_id: str):
    """Run all tests using QA Agent."""
    # Placeholder implementation
    return {"test_results": "All tests completed"}


def display_test_results(test_results):
    """Display test results."""
    console.print("[green]Testing completed![/green]")
    console.print(json.dumps(test_results, indent=2))


def get_project_status(project_id: str):
    """Get project status."""
    # Placeholder implementation
    return {"status": "Project status retrieved"}


def display_project_status(project_status):
    """Display project status."""
    console.print("[green]Project status:[/green]")
    console.print(json.dumps(project_status, indent=2))


if __name__ == "__main__":
    app()

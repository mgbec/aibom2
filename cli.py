#!/usr/bin/env python3
"""
CLI tool for local testing and development of the AIBOM Agent System.
"""

import asyncio
import sys
from pathlib import Path

import click
from loguru import logger
from rich.console import Console
from rich.panel import Panel

from aibom_agent.core.agent_orchestrator import AIBOMAgentOrchestrator
from aibom_agent.config.settings import Settings

console = Console()


@click.group()
def cli():
    """AIBOM Agent System CLI - Local development and testing tool."""
    pass


@cli.command()
@click.option(
    "--models",
    "-m",
    multiple=True,
    help="Hugging Face model names to analyze (can specify multiple)",
)
@click.option(
    "--output-dir",
    "-o",
    default="./reports",
    help="Output directory for generated reports",
)
@click.option(
    "--config-file",
    "-c",
    help="Path to configuration file",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def analyze(
    models: tuple[str, ...],
    output_dir: str,
    config_file: str | None,
    verbose: bool,
) -> None:
    """Analyze AI models locally (for development/testing)."""
    
    # Configure logging
    logger.remove()
    log_level = "DEBUG" if verbose else "INFO"
    logger.add(sys.stderr, level=log_level, format="{time} | {level} | {message}")
    
    console.print(
        Panel.fit(
            "[bold blue]🤖 AIBOM Agent System - Local Analysis[/bold blue]\n"
            "Development and Testing Mode",
            border_style="blue",
        )
    )
    
    try:
        # Load configuration
        settings = Settings.load(config_file)
        settings.output_dir = output_dir
        
        # Initialize orchestrator
        orchestrator = AIBOMAgentOrchestrator(settings, "cli-session")
        
        # Run the analysis
        if models:
            asyncio.run(run_local_analysis(orchestrator, list(models)))
        else:
            console.print("[yellow]No models specified. Use --models to specify models to analyze.[/yellow]")
            console.print("\nExample:")
            console.print("  python cli.py analyze -m microsoft/DialoGPT-medium -m facebook/blenderbot-400M-distill")
            
    except Exception as e:
        logger.error(f"Failed to run local analysis: {e}")
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--port", "-p", default=8000, help="Port to run the development server on")
def serve(port: int) -> None:
    """Run the AgentCore app locally for development."""
    console.print(
        Panel.fit(
            "[bold green]🚀 Starting AIBOM Agent Development Server[/bold green]\n"
            f"Server will run on port {port}",
            border_style="green",
        )
    )
    
    try:
        # Import and run the main app
        from main import app
        app.run(port=port)
        
    except Exception as e:
        logger.error(f"Failed to start development server: {e}")
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
def test_payload() -> None:
    """Test the agent with sample payloads."""
    console.print(
        Panel.fit(
            "[bold yellow]🧪 Testing AIBOM Agent with Sample Payloads[/bold yellow]",
            border_style="yellow",
        )
    )
    
    # Sample payloads for testing
    test_payloads = [
        {
            "action": "analyze_model",
            "model_name": "microsoft/DialoGPT-medium"
        },
        {
            "action": "compare_models",
            "model_names": ["microsoft/DialoGPT-medium", "facebook/blenderbot-400M-distill"]
        }
    ]
    
    try:
        from main import invoke
        
        # Mock context object
        class MockContext:
            def __init__(self):
                self.session_id = "test-session"
        
        context = MockContext()
        
        for i, payload in enumerate(test_payloads, 1):
            console.print(f"\n[bold]Test {i}: {payload['action']}[/bold]")
            console.print(f"Payload: {payload}")
            
            try:
                result = invoke(payload, context)
                console.print(f"[green]✓ Success:[/green] {result}")
            except Exception as e:
                console.print(f"[red]✗ Failed:[/red] {e}")
                
    except Exception as e:
        logger.error(f"Failed to run payload tests: {e}")
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
def config() -> None:
    """Show current configuration."""
    try:
        settings = Settings.load()
        
        console.print(
            Panel.fit(
                "[bold blue]⚙️ AIBOM Agent Configuration[/bold blue]",
                border_style="blue",
            )
        )
        
        console.print(f"[bold]AWS Settings:[/bold]")
        console.print(f"  Region: {settings.aws.region}")
        console.print(f"  Bedrock Agent ID: {settings.aws.bedrock_agent_id or 'Not set'}")
        console.print(f"  S3 Bucket: {settings.aws.s3_bucket or 'Not set'}")
        
        console.print(f"\n[bold]Hugging Face Settings:[/bold]")
        console.print(f"  Token: {'Set' if settings.huggingface.token else 'Not set'}")
        console.print(f"  Cache Dir: {settings.huggingface.cache_dir}")
        
        console.print(f"\n[bold]Output Settings:[/bold]")
        console.print(f"  Output Dir: {settings.output_dir}")
        console.print(f"  Temp Dir: {settings.temp_dir}")
        
        console.print(f"\n[bold]Debug Mode:[/bold] {settings.debug}")
        
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        sys.exit(1)


async def run_local_analysis(
    orchestrator: AIBOMAgentOrchestrator, 
    models: list[str]
) -> None:
    """Run the AIBOM analysis locally."""
    
    logger.info(f"Starting local analysis for {len(models)} models")
    
    # Initialize the orchestrator
    await orchestrator.initialize()
    
    if len(models) == 1:
        # Single model analysis
        result = await orchestrator.analyze_single_model(models[0])
        console.print(f"[green]✓[/green] Analysis completed for {models[0]}")
        console.print(f"Report saved to: {result.report_path}")
        
    else:
        # Comparative analysis
        result = await orchestrator.compare_models(models)
        console.print(f"[green]✓[/green] Comparative analysis completed for {len(models)} models")
        console.print(f"Comparison report saved to: {result.report_path}")
    
    # Display summary
    console.print("\n[bold]Analysis Summary:[/bold]")
    console.print(f"• Models analyzed: {len(models)}")
    console.print(f"• Security issues found: {result.security_issues_count}")
    console.print(f"• Compliance gaps: {result.compliance_gaps_count}")
    console.print(f"• Report location: {result.report_path}")


if __name__ == "__main__":
    cli()
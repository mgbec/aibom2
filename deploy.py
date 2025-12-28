#!/usr/bin/env python3
"""
Deployment script for AIBOM Agent System using AgentCore CLI.
"""

import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    console.print(f"[blue]Running:[/blue] {description}")
    console.print(f"[dim]Command: {command}[/dim]")
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        console.print(f"[green]✓[/green] {description} completed successfully")
        if result.stdout:
            console.print(f"[dim]{result.stdout}[/dim]")
        return True
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗[/red] {description} failed")
        console.print(f"[red]Error:[/red] {e.stderr}")
        return False


def main():
    """Main deployment function."""
    console.print(
        Panel.fit(
            "[bold blue]🚀 AIBOM Agent System Deployment[/bold blue]\n"
            "Deploying to AWS AgentCore Runtime",
            border_style="blue",
        )
    )
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        console.print("[red]Error: main.py not found. Please run from project root.[/red]")
        sys.exit(1)
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        console.print("[red]Error: requirements.txt not found.[/red]")
        sys.exit(1)
    
    console.print("\n[bold]Step 1: Checking AgentCore CLI installation[/bold]")
    
    # Check if agentcore CLI is installed
    try:
        result = subprocess.run(
            ["agentcore", "--help"],
            capture_output=True,
            text=True,
            check=True
        )
        console.print(f"[green]✓[/green] AgentCore CLI found and working")
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("[red]✗[/red] AgentCore CLI not found")
        console.print("\nPlease install the AgentCore starter toolkit:")
        console.print("  pip install bedrock-agentcore-starter-toolkit")
        sys.exit(1)
    
    console.print("\n[bold]Step 2: Configuring the agent[/bold]")
    
    # Run agentcore configure with proper parameters
    console.print("Configuring AgentCore agent...")
    
    configure_cmd = [
        "agentcore", "configure", "--create",
        "--entrypoint", "main.py",
        "--name", "aibom_agent_system",
        "--requirements-file", "requirements.txt",
        "--deployment-type", "direct_code_deploy",
        "--runtime", "PYTHON_3_11",
        "--non-interactive"
    ]
    
    try:
        result = subprocess.run(configure_cmd, check=True, capture_output=True, text=True)
        console.print("[green]✓[/green] Agent configuration completed")
        if result.stdout:
            console.print(f"[dim]{result.stdout}[/dim]")
    except subprocess.CalledProcessError as e:
        console.print("[red]✗[/red] Agent configuration failed")
        console.print(f"[red]Error:[/red] {e.stderr}")
        console.print("\nYou can also configure manually with:")
        console.print("  agentcore configure --create --entrypoint main.py --name aibom_agent_system")
        sys.exit(1)
    
    console.print("\n[bold]Step 3: Deploying the agent[/bold]")
    
    # Run agentcore deploy
    if not run_command("agentcore deploy --agent aibom_agent_system", "Agent deployment"):
        console.print("\n[red]Deployment failed. Please check the error messages above.[/red]")
        sys.exit(1)
    
    console.print("\n[bold]Step 4: Checking deployment status[/bold]")
    
    # Check status
    if not run_command("agentcore status", "Deployment status check"):
        console.print("[yellow]Warning: Could not check deployment status[/yellow]")
    
    console.print(
        Panel.fit(
            "[bold green]🎉 Deployment Complete![/bold green]\n"
            "Your AIBOM Agent System is now running on AWS AgentCore Runtime.\n\n"
            "Next steps:\n"
            "• Test your agent with: agentcore invoke\n"
            "• View logs with: agentcore logs\n"
            "• Monitor with: agentcore status",
            border_style="green",
        )
    )


if __name__ == "__main__":
    main()
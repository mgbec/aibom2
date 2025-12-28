#!/usr/bin/env python3
"""
Test script for the AIBOM Agent System.
"""

import asyncio
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()


def test_agentcore_entrypoint():
    """Test the AgentCore entrypoint function."""
    console.print(
        Panel.fit(
            "[bold blue]🧪 Testing AgentCore Entrypoint[/bold blue]",
            border_style="blue",
        )
    )
    
    try:
        from main import invoke
        
        # Mock context object
        class MockContext:
            def __init__(self):
                self.session_id = "test-session-123"
        
        context = MockContext()
        
        # Test single model analysis
        console.print("\n[bold]Test 1: Single Model Analysis[/bold]")
        payload1 = {
            "action": "analyze_model",
            "model_name": "microsoft/DialoGPT-medium"
        }
        
        console.print(f"Payload: {json.dumps(payload1, indent=2)}")
        
        try:
            result1 = invoke(payload1, context)
            console.print(f"[green]✓ Success:[/green]")
            console.print(json.dumps(result1, indent=2))
        except Exception as e:
            console.print(f"[red]✗ Failed:[/red] {e}")
        
        # Test model comparison
        console.print("\n[bold]Test 2: Model Comparison[/bold]")
        payload2 = {
            "action": "compare_models",
            "model_names": ["microsoft/DialoGPT-medium", "facebook/blenderbot-400M-distill"]
        }
        
        console.print(f"Payload: {json.dumps(payload2, indent=2)}")
        
        try:
            result2 = invoke(payload2, context)
            console.print(f"[green]✓ Success:[/green]")
            console.print(json.dumps(result2, indent=2))
        except Exception as e:
            console.print(f"[red]✗ Failed:[/red] {e}")
        
        # Test invalid action
        console.print("\n[bold]Test 3: Invalid Action[/bold]")
        payload3 = {
            "action": "invalid_action",
            "model_name": "test"
        }
        
        console.print(f"Payload: {json.dumps(payload3, indent=2)}")
        
        try:
            result3 = invoke(payload3, context)
            console.print(f"[yellow]Expected error:[/yellow]")
            console.print(json.dumps(result3, indent=2))
        except Exception as e:
            console.print(f"[red]Unexpected error:[/red] {e}")
        
    except ImportError as e:
        console.print(f"[red]Import error:[/red] {e}")
        console.print("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        console.print(f"[red]Test failed:[/red] {e}")


def test_health_check():
    """Test the health check endpoint."""
    console.print(
        Panel.fit(
            "[bold green]🏥 Testing Health Check[/bold green]",
            border_style="green",
        )
    )
    
    try:
        from main import health_check
        
        result = health_check()
        console.print(f"[green]✓ Health check passed:[/green]")
        console.print(json.dumps(result, indent=2))
        
    except Exception as e:
        console.print(f"[red]✗ Health check failed:[/red] {e}")


def test_configuration():
    """Test configuration loading."""
    console.print(
        Panel.fit(
            "[bold yellow]⚙️ Testing Configuration[/bold yellow]",
            border_style="yellow",
        )
    )
    
    try:
        from aibom_agent.config.settings import Settings
        
        settings = Settings.load()
        
        console.print(f"[green]✓ Configuration loaded successfully[/green]")
        console.print(f"AWS Region: {settings.aws.region}")
        console.print(f"Output Dir: {settings.output_dir}")
        console.print(f"Debug Mode: {settings.debug}")
        
        # Test directory creation
        settings.ensure_directories()
        console.print(f"[green]✓ Directories created/verified[/green]")
        
    except Exception as e:
        console.print(f"[red]✗ Configuration test failed:[/red] {e}")


def main():
    """Run all tests."""
    console.print(
        Panel.fit(
            "[bold magenta]🚀 AIBOM Agent System Test Suite[/bold magenta]\n"
            "Testing core functionality before deployment",
            border_style="magenta",
        )
    )
    
    # Run tests
    test_configuration()
    test_health_check()
    test_agentcore_entrypoint()
    
    console.print(
        Panel.fit(
            "[bold blue]📋 Test Summary[/bold blue]\n"
            "Review the results above to ensure everything is working correctly.\n"
            "If all tests pass, you can proceed with deployment using 'python deploy.py'",
            border_style="blue",
        )
    )


if __name__ == "__main__":
    main()
# AI Bill of Materials Agent System

An intelligent agent system that automatically generates, compares, and analyzes AI Bill of Materials (AIBOMs) for Hugging Face models using the OWASP AIBOM Generator and AWS AgentCore runtime.

## Overview

This project creates an autonomous agent that:
- Fetches model information from Hugging Face
- Generates AIBOMs using the OWASP AIBOM Generator
- Performs comparative analysis between different models
- Identifies security risks and compliance gaps
- Generates detailed comparison reports

## Architecture

- **AWS AgentCore Runtime**: Orchestrates agent execution and tool coordination
- **OWASP AIBOM Generator**: Generates standardized AIBOMs for ML models
- **Hugging Face Integration**: Fetches model metadata and artifacts
- **Comparison Engine**: Analyzes differences in model components and risks

## Key Features

- 🤖 **AgentCore Runtime**: Intelligent workflow orchestration with multi-step reasoning
- 🔧 **Automated AIBOM Generation**: Uses OWASP standard for ML model bills of materials
- 🔍 **AI-Powered Analysis**: Bedrock Agent provides intelligent security insights
- 📊 **Comprehensive Reporting**: Interactive HTML reports with visualizations
- ☁️ **Cloud-Native**: Fully deployable to AWS with serverless execution
- 🔒 **Security-First**: Identifies vulnerabilities, unsafe formats, and compliance gaps

## Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure

# Deploy infrastructure
python deploy.py

# Run the agent
python main.py
```

## Project Structure

```
├── aibom_agent/
│   ├── core/               # Core orchestration logic
│   │   └── agent_orchestrator.py
│   ├── services/           # Service implementations
│   │   ├── huggingface_service.py
│   │   ├── aibom_generator.py
│   │   ├── bedrock_agent.py
│   │   ├── comparison_engine.py
│   │   └── report_generator.py
│   ├── models/             # Data models
│   │   └── analysis_result.py
│   ├── config/             # Configuration
│   │   └── settings.py
│   └── templates/          # HTML report templates
├── main.py                 # AgentCore runtime entrypoint
├── cli.py                  # Local development CLI
├── deploy.py               # Deployment script
├── requirements.txt        # Python dependencies
└── reports/                # Generated reports output
```

## AgentCore Integration

This system uses **AWS AgentCore Runtime** for production deployment:

- **`main.py`**: AgentCore entrypoint with `@app.entrypoint` decorator
- **Intelligent Orchestration**: Multi-step reasoning for AIBOM analysis
- **Session Management**: Automatic session handling and state persistence
- **Streaming Support**: Real-time analysis progress updates
- **Production Ready**: Managed runtime with auto-scaling and monitoring

## Usage

### Local Development

```bash
# Test locally with CLI
python cli.py analyze -m microsoft/DialoGPT-medium

# Compare multiple models
python cli.py analyze -m microsoft/DialoGPT-medium -m facebook/blenderbot-400M-distill

# Run development server
python cli.py serve --port 8000

# Test with sample payloads
python cli.py test-payload
```

### AgentCore Runtime (Production)

```bash
# Configure and deploy
python deploy.py

# Or manually:
agentcore configure
agentcore deploy

# Test the deployed agent
agentcore invoke --payload '{"action": "analyze_model", "model_name": "microsoft/DialoGPT-medium"}'

# Monitor
agentcore status
agentcore logs
```
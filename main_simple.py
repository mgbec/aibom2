#!/usr/bin/env python3
"""
Simple AIBOM Agent for testing deployment
"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Initialize AgentCore app
app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload, context):
    """Simple test entrypoint."""
    return {
        "success": True,
        "message": "AIBOM Agent is working!",
        "payload_received": payload,
        "session_id": getattr(context, 'session_id', 'unknown')
    }


# @app.ping
# def health_check():
#     """Simple health check."""
#     return None


if __name__ == "__main__":
    app.run()
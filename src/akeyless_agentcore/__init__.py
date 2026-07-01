"""Fetch Akeyless secrets at runtime on AWS Bedrock AgentCore."""

from akeyless_agentcore.client import (
    AkeylessRuntimeClient,
    get_default_client,
    get_secret,
    get_secret_sync,
)

__all__ = [
    "AkeylessRuntimeClient",
    "get_default_client",
    "get_secret",
    "get_secret_sync",
]

__version__ = "0.2.0"

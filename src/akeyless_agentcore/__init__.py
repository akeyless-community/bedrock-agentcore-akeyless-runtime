"""Fetch Akeyless secrets at runtime on AWS Bedrock AgentCore."""

from akeyless_agentcore.client import (
    AkeylessRuntimeClient,
    DynamicSecretOptions,
    GetSecretOptions,
    RotatedSecretOptions,
    get_default_client,
    get_secret,
)

__all__ = [
    "AkeylessRuntimeClient",
    "DynamicSecretOptions",
    "GetSecretOptions",
    "RotatedSecretOptions",
    "get_default_client",
    "get_secret",
]

__version__ = "0.3.0"

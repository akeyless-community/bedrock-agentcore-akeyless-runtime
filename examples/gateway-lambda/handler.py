"""AgentCore Gateway Lambda target for Akeyless secret tools.

Package this file with akeyless-agentcore-runtime and deploy as a Lambda.
Register with Gateway using GATEWAY_TOOL_SCHEMA from the same package.

See examples/gateway-lambda/setup_gateway_target.py for a setup script.
"""

from akeyless_agentcore.tools.gateway import gateway_lambda_handler

lambda_handler = gateway_lambda_handler

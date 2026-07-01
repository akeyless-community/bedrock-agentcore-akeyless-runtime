"""Add the Akeyless secrets Lambda as an AgentCore Gateway target.

Prerequisites:
  - An existing Gateway (see AgentCore Gateway quickstart)
  - gateway_config.json with gateway_id and region
  - Lambda function deployed from handler.py

Usage:
  python setup_gateway_target.py --lambda-arn arn:aws:lambda:...
"""

from __future__ import annotations

import argparse
import json
import sys

from akeyless_agentcore.tools.gateway import GATEWAY_TOOL_SCHEMA


def main() -> None:
    parser = argparse.ArgumentParser(description="Register Akeyless Lambda with AgentCore Gateway")
    parser.add_argument("--lambda-arn", required=True, help="ARN of the deployed Lambda function")
    parser.add_argument(
        "--config",
        default="gateway_config.json",
        help="Gateway config file from setup_gateway.py",
    )
    args = parser.parse_args()

    try:
        from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
    except ImportError:
        print("Install gateway extras: pip install 'akeyless-agentcore-runtime[gateway]'")
        sys.exit(1)

    with open(args.config, encoding="utf-8") as handle:
        config = json.load(handle)

    client = GatewayClient(region_name=config["region"])
    gateway = client.client.get_gateway(gatewayIdentifier=config["gateway_id"])

    target_payload = {
        "lambdaArn": args.lambda_arn,
        "toolSchema": GATEWAY_TOOL_SCHEMA,
    }

    target = client.create_mcp_gateway_target(
        gateway=gateway,
        name="AkeylessSecrets",
        target_type="lambda",
        target_payload=target_payload,
    )

    print(f"Gateway target created: {target['targetId']}")
    print("Tools: list_akeyless_secrets, get_akeyless_secret")


if __name__ == "__main__":
    main()

"""
SKILL DNA — Amazon Bedrock AgentCore Deployment Script

This script documents and automates the AgentCore deployment steps.
It uses the Bedrock AgentCore boto3 client to create/update the runtime.

Prerequisites:
    1. Docker installed and running
    2. AWS CLI configured with ECR push permissions
    3. pip install boto3 python-dotenv

Usage:
    python deploy_agentcore.py --action build     # Build Docker image
    python deploy_agentcore.py --action push      # Push to ECR
    python deploy_agentcore.py --action deploy    # Deploy to AgentCore
    python deploy_agentcore.py --action all       # Full pipeline

Reference:
    https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/getting-started-custom.html
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

import boto3

AWS_REGION      = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
AWS_ACCOUNT_ID  = None   # filled at runtime
ECR_REPO_NAME   = "skill-dna-agent"
AGENTCORE_NAME  = "skill-dna-pipeline"
IMAGE_TAG       = "latest"


def get_account_id() -> str:
    global AWS_ACCOUNT_ID
    if not AWS_ACCOUNT_ID:
        sts = boto3.client("sts", region_name=AWS_REGION)
        AWS_ACCOUNT_ID = sts.get_caller_identity()["Account"]
    return AWS_ACCOUNT_ID


def ecr_uri() -> str:
    return f"{get_account_id()}.dkr.ecr.{AWS_REGION}.amazonaws.com/{ECR_REPO_NAME}:{IMAGE_TAG}"


def run(cmd: str, check: bool = True) -> int:
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True)
    if check and result.returncode != 0:
        print(f"  ❌ Command failed: {result.returncode}")
        sys.exit(result.returncode)
    return result.returncode


def action_build():
    """Build the Docker image locally."""
    print("\n🔨 Building Docker image...")
    project_root = Path(__file__).parent
    run(f"docker build -t {ECR_REPO_NAME}:{IMAGE_TAG} {project_root}")
    print(f"  ✅ Image built: {ECR_REPO_NAME}:{IMAGE_TAG}")

    # Quick local test
    print("\n🧪 Testing /ping endpoint locally...")
    run(f"docker run --rm -d -p 8080:8080 --env-file .env --name skill-dna-test {ECR_REPO_NAME}:{IMAGE_TAG}")
    import time; time.sleep(4)
    run("curl -sf http://localhost:8080/ping && echo '' || echo 'ping failed'", check=False)
    run("docker stop skill-dna-test", check=False)


def action_push():
    """Tag and push image to Amazon ECR."""
    print("\n📤 Pushing to Amazon ECR...")
    ecr = boto3.client("ecr", region_name=AWS_REGION)

    # Create repo if needed
    try:
        ecr.create_repository(repositoryName=ECR_REPO_NAME, imageTagMutability="MUTABLE")
        print(f"  ✅ ECR repo created: {ECR_REPO_NAME}")
    except ecr.exceptions.RepositoryAlreadyExistsException:
        print(f"  ℹ️  ECR repo exists: {ECR_REPO_NAME}")

    # Login + tag + push
    run(f"aws ecr get-login-password --region {AWS_REGION} | docker login --username AWS --password-stdin {get_account_id()}.dkr.ecr.{AWS_REGION}.amazonaws.com")
    run(f"docker tag {ECR_REPO_NAME}:{IMAGE_TAG} {ecr_uri()}")
    run(f"docker push {ecr_uri()}")
    print(f"  ✅ Pushed: {ecr_uri()}")


def action_deploy():
    """Deploy to Amazon Bedrock AgentCore Runtime."""
    print("\n🚀 Deploying to Amazon Bedrock AgentCore Runtime...")

    # AgentCore uses bedrock-agentcore-control-plane
    client = boto3.client("bedrock-agentcore-control-plane", region_name=AWS_REGION)

    runtime_config = {
        "name": AGENTCORE_NAME,
        "description": "SKILL DNA multi-agent craft knowledge pipeline",
        "containerConfig": {
            "containerUri": ecr_uri(),
            "networkMode": "awsvpc",
        },
        "executionRoleArn": f"arn:aws:iam::{get_account_id()}:role/AmazonBedrockAgentCoreExecutionRole",
    }

    try:
        # Try to create
        response = client.create_agent_runtime(**runtime_config)
        runtime_id = response["agentRuntimeId"]
        print(f"  ✅ AgentCore runtime created: {runtime_id}")
    except client.exceptions.ConflictException:
        # Already exists — update it
        print(f"  ℹ️  Runtime exists — updating...")
        runtimes = client.list_agent_runtimes()
        runtime_id = next(
            (r["agentRuntimeId"] for r in runtimes["agentRuntimes"] if r["name"] == AGENTCORE_NAME),
            None
        )
        if runtime_id:
            client.update_agent_runtime(agentRuntimeId=runtime_id, **{k: v for k, v in runtime_config.items() if k != "name"})
            print(f"  ✅ AgentCore runtime updated: {runtime_id}")
        else:
            print("  ❌ Could not find existing runtime to update")
            sys.exit(1)

    # Save runtime ID
    Path(".agentcore_runtime_id").write_text(runtime_id)
    print(f"\n  Runtime ID saved to .agentcore_runtime_id")
    print(f"  Invoke endpoint: https://bedrock-agentcore.{AWS_REGION}.amazonaws.com/runtimes/{runtime_id}/invocations")


def main():
    ap = argparse.ArgumentParser(prog="python deploy_agentcore.py")
    ap.add_argument("--action", choices=["build", "push", "deploy", "all"], default="all")
    args = ap.parse_args()

    print(f"\n{'='*55}")
    print(f"  SKILL DNA → Amazon Bedrock AgentCore Deployment")
    print(f"  Region: {AWS_REGION}  Account: {get_account_id()}")
    print(f"{'='*55}")

    if args.action in ("build", "all"):
        action_build()
    if args.action in ("push", "all"):
        action_push()
    if args.action in ("deploy", "all"):
        action_deploy()

    print("\n✅ Deployment complete\n")


if __name__ == "__main__":
    main()

import uuid
from datetime import datetime, timezone

import boto3
from fastmcp import FastMCP

from selfmcp.config import settings

mcp = FastMCP("diary")


@mcp.tool()
async def record_entry(content: str, title: str | None = None) -> str:
    """Record a new diary entry and store it in S3.

    Args:
        content: The diary entry text to store.
        title: Optional title for the entry. Defaults to a timestamp-based name.
    """
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H-%M-%S")
    key = f"entries/{timestamp}_{uuid.uuid4().hex[:8]}.md"

    header = f"# {title}\n\n" if title else ""
    date_line = f"*{now.strftime('%Y-%m-%d %H:%M:%S UTC')}*\n\n"
    body = header + date_line + content

    s3 = boto3.client("s3", region_name=settings.aws_region)
    s3.put_object(
        Bucket=settings.s3_bucket_name,
        Key=key,
        Body=body.encode("utf-8"),
        ContentType="text/markdown",
    )

    return f"Entry stored at s3://{settings.s3_bucket_name}/{key}"


@mcp.tool()
async def query_diary(question: str) -> str:
    """Query your diary using natural language via a Bedrock agent.

    Args:
        question: A natural language question about your diary entries.
    """
    client = boto3.client("bedrock-agent-runtime", region_name=settings.aws_region)

    response = client.invoke_agent(
        agentId=settings.bedrock_agent_id,
        agentAliasId=settings.bedrock_agent_alias_id,
        sessionId=uuid.uuid4().hex,
        inputText=question,
    )

    # Collect streamed chunks
    output_parts = []
    for event in response["completion"]:
        if "chunk" in event:
            output_parts.append(event["chunk"]["bytes"].decode("utf-8"))

    return "".join(output_parts) or "No response from agent."

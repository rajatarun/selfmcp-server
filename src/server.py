"""
Tarun's Personal MCP Server
Aggregates Instagram photography, hiking trails, and travel reviews.
Deployed as an AWS Lambda function via SAM + Mangum.
"""
from fastmcp import FastMCP
from mangum import Mangum

from tools.hiking import get_hiking_activity
from tools.personal_facts import get_personal_facts
from tools.photography import get_photography
from tools.travel import get_travel_reviews

mcp = FastMCP(
    name="tarun-personal-mcp",
    instructions=(
        "This server exposes personal data for Tarun Raja: "
        "Instagram photography with AI descriptions, hiking trail history, "
        "travel destination reviews, and general personal facts. "
        "Use these tools to answer questions about Tarun's outdoor activities, "
        "travel experiences, photography, and professional background."
    ),
)

mcp.tool()(get_photography)
mcp.tool()(get_hiking_activity)
mcp.tool()(get_travel_reviews)
mcp.tool()(get_personal_facts)

# Lambda entrypoint — Mangum bridges ASGI to Lambda proxy events
handler = Mangum(mcp.get_asgi_app(), lifespan="off")

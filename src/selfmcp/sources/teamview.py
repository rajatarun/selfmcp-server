from fastmcp import FastMCP
import httpx

from selfmcp.config import settings

mcp = FastMCP("teamview")


@mcp.tool()
async def list_teams() -> list[dict]:
    """List all available agentic teams that can be invoked."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.teamview_base_url}/teams",
            headers={"Authorization": f"Bearer {settings.teamview_api_key}"},
            timeout=15.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def invoke_team(task: str, team_id: str) -> str:
    """Dispatch a task to a specific agentic team and return its response.

    Args:
        task: A description of the task for the team to handle.
        team_id: The identifier of the team to invoke.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.teamview_base_url}/teams/{team_id}/invoke",
            json={"task": task},
            headers={"Authorization": f"Bearer {settings.teamview_api_key}"},
            timeout=120.0,
        )
        response.raise_for_status()
        data = response.json()

    return data.get("result", data.get("response", str(data)))

from fastmcp import FastMCP
import httpx

from selfmcp.config import settings

mcp = FastMCP("adaptive-rag")


@mcp.tool()
async def query_knowledge_base(query: str, collection: str | None = None) -> str:
    """Query the Adaptive RAG knowledge base for relevant information.

    Args:
        query: The search query or question to answer.
        collection: Optional name of the collection/index to search within.
    """
    payload: dict = {"query": query}
    if collection is not None:
        payload["collection"] = collection

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.adaptive_rag_base_url}/query",
            json=payload,
            headers={"Authorization": f"Bearer {settings.adaptive_rag_api_key}"},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

    return data.get("answer", data.get("result", str(data)))

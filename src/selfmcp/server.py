from fastmcp import FastMCP

from selfmcp.sources.adaptive_rag import mcp as adaptive_rag_mcp
from selfmcp.sources.teamview import mcp as teamview_mcp

mcp = FastMCP("selfmcp-server")

mcp.mount("rag", adaptive_rag_mcp)
mcp.mount("teamview", teamview_mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

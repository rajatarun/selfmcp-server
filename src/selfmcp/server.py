from fastmcp import FastMCP

from selfmcp.sources.diary import mcp as diary_mcp

mcp = FastMCP("selfmcp-server")

mcp.mount("diary", diary_mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

import os

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

import server

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))

    old = server.mcp
    mcp = FastMCP(
        "stock-trends",
        host="0.0.0.0",
        port=port,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=False,
        ),
    )
    mcp._tool_manager = old._tool_manager
    mcp._resource_manager = old._resource_manager
    mcp._prompt_manager = old._prompt_manager

    print(f"Starting stock-trends-mcp on 0.0.0.0:{port} via SSE")
    mcp.run(transport="sse")
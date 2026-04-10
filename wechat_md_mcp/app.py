from typing import Any, Dict, List, Tuple

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .tooling import build_tools, handle_tool_call


def create_server(server_name: str, version: str) -> Tuple[Server, List[Tool]]:
    server = Server(server_name, version)
    tools = build_tools()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
        return handle_tool_call(name, arguments)

    return server, tools


async def serve_mcp(server: Server, server_name: str, server_version: str) -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=server_name,
                server_version=server_version,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(tools_changed=True),
                    experimental_capabilities={},
                ),
            ),
        )

#!/usr/bin/env python3
import argparse
import asyncio
import os
import sys
from importlib.metadata import version as _pkg_version
from pathlib import Path
from typing import Any, Dict


def _maybe_reexec_with_local_venv() -> None:
    """
    If this script is launched directly with a Python that doesn't have `mcp`,
    re-exec with the local project venv interpreter when available.
    """
    if __name__ != "__main__":
        return
    if os.environ.get("WECHAT_MCP_NO_REEXEC") == "1":
        return

    try:
        __import__("mcp")
        return
    except ModuleNotFoundError:
        pass

    venv_python = Path(__file__).resolve().parent / ".venv" / "bin" / "python"
    if not venv_python.is_file():
        return
    if Path(sys.executable).resolve() == venv_python.resolve():
        return

    os.environ["WECHAT_MCP_NO_REEXEC"] = "1"
    os.execv(str(venv_python), [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]])


_maybe_reexec_with_local_venv()

from mcp.server import Server
from mcp.types import TextContent, Tool

from wechat_md_mcp import SERVER_NAME, THEMES, ensure_cache_dir, inline_format, parse_markdown, save_html_cache
from wechat_md_mcp.app import create_server, serve_mcp
from wechat_md_mcp.tooling import handle_tool_call

try:
    SERVER_VERSION = _pkg_version("wechat-md-mcp-server")
except Exception:
    SERVER_VERSION = "0.1.0"

server: Server
TOOLS: list[Tool]
server, TOOLS = create_server(SERVER_NAME, SERVER_VERSION)


async def list_tools() -> list[Tool]:
    return TOOLS


async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    return handle_tool_call(name, arguments)


async def serve() -> None:
    await serve_mcp(server=server, server_name=SERVER_NAME, server_version=SERVER_VERSION)


def main() -> None:
    help_epilog = """Examples:
  wechat-md-mcp-server
      Start MCP stdio server (default behavior).

  wechat-md-mcp-server --list-tools
      Print tool names and exit.

  wechat-md-mcp-server --version
      Print version and exit.
"""
    parser = argparse.ArgumentParser(
        prog="wechat-md-mcp-server",
        description="Markdown to WeChat HTML MCP server",
        epilog=help_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {SERVER_VERSION}")
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="Print available tool names and exit.",
    )

    # Some MCP clients append transport/runtime flags. Ignore unknown args so
    # the server still starts over stdio instead of exiting on argparse errors.
    args, _unknown = parser.parse_known_args()

    if args.list_tools:
        print("\n".join(tool.name for tool in TOOLS))
        return

    # Keep stdout clean for MCP JSON-RPC traffic.
    sys.stdout.reconfigure(write_through=True)
    asyncio.run(serve())


if __name__ == "__main__":
    main()

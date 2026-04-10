import json
import webbrowser
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from mcp.types import TextContent, Tool

from .cache import save_html_cache
from .markdown_renderer import parse_markdown
from .themes import THEMES, THEME_DESCRIPTIONS


def build_tools() -> List[Tool]:
    return [
        Tool(
            name="convert_markdown_to_wechat_html",
            description="Convert Markdown to WeChat-friendly HTML with inline styles for copy/paste publishing workflows.",
            inputSchema={
                "type": "object",
                "properties": {
                    "markdown": {"type": "string", "description": "Source markdown text"},
                    "theme": {
                        "type": "string",
                        "description": "Theme name: default | tech | warm | apple | wechat-native",
                        "enum": list(THEMES.keys()),
                        "default": "default",
                    },
                    "title": {"type": "string", "description": "Optional article title rendered as h1"},
                },
                "required": ["markdown"],
            },
        ),
        Tool(
            name="open_wechat_html_in_browser",
            description="Open a cached WeChat HTML file in the default browser. Select all and copy in the browser, then paste into WeChat editor as rich text.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cache_path": {
                        "type": "string",
                        "description": "cache_path returned by convert_markdown_to_wechat_html",
                    },
                },
                "required": ["cache_path"],
            },
        ),
        Tool(
            name="list_wechat_themes",
            description="List available rendering themes.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


def _require_non_empty_string(arguments: Dict[str, Any], key: str) -> str:
    value = arguments.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} is required and must be a non-empty string.")
    return value


def _parse_theme(arguments: Dict[str, Any]) -> str:
    theme = arguments.get("theme", "default")
    if not isinstance(theme, str) or theme not in THEMES:
        raise ValueError(f"Invalid theme: {theme}. Available: {', '.join(sorted(THEMES.keys()))}")
    return theme


def _parse_optional_title(arguments: Dict[str, Any]) -> Optional[str]:
    title = arguments.get("title")
    if title is None:
        return None
    if not isinstance(title, str):
        raise ValueError("title must be a string when provided.")
    return title


def _handle_list_wechat_themes(_arguments: Dict[str, Any]) -> List[TextContent]:
    themes_info = [{"name": name, "description": desc} for name, desc in THEME_DESCRIPTIONS.items()]
    return [TextContent(type="text", text=json.dumps({"themes": themes_info}, ensure_ascii=False, indent=2))]


def _handle_open_wechat_html_in_browser(arguments: Dict[str, Any]) -> List[TextContent]:
    cache_path = _require_non_empty_string(arguments, "cache_path")
    p = Path(cache_path)
    if not p.is_file():
        raise ValueError(f"File not found: {cache_path}")
    webbrowser.open(p.as_uri())
    return [TextContent(type="text", text=json.dumps({"ok": True}, ensure_ascii=False))]


def _handle_convert_markdown_to_wechat_html(arguments: Dict[str, Any]) -> List[TextContent]:
    markdown = _require_non_empty_string(arguments, "markdown")
    theme = _parse_theme(arguments)
    title = _parse_optional_title(arguments)
    html = parse_markdown(markdown, theme_name=theme, title=title)
    cache_path = save_html_cache(html)
    return [TextContent(type="text", text=json.dumps({"html": html, "cache_path": cache_path}, ensure_ascii=False))]


TOOL_HANDLERS: Dict[str, Callable[[Dict[str, Any]], List[TextContent]]] = {
    "list_wechat_themes": _handle_list_wechat_themes,
    "open_wechat_html_in_browser": _handle_open_wechat_html_in_browser,
    "convert_markdown_to_wechat_html": _handle_convert_markdown_to_wechat_html,
}


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        raise ValueError(f"Unknown tool: {name}")
    return handler(arguments)

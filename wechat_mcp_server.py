#!/usr/bin/env python3
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from html import escape
from typing import Any, Dict, List, Optional

PROTOCOL_VERSION = "2024-11-05"

THEMES = {
    "default": {
        "article": "max-width: 860px; margin: 0 auto; color: #1f2329; font-size: 16px; line-height: 1.8;",
        "h1": "font-size: 30px; line-height: 1.35; margin: 1.3em 0 0.7em; color: #102a43;",
        "h2": "font-size: 24px; line-height: 1.4; margin: 1.2em 0 0.65em; color: #16324f; border-left: 4px solid #1f6feb; padding-left: 10px;",
        "h3": "font-size: 20px; line-height: 1.45; margin: 1.1em 0 0.55em; color: #1f4b7a;",
        "p": "margin: 0.85em 0;",
        "li": "margin: 0.35em 0;",
        "blockquote": "margin: 1em 0; padding: 0.8em 1em; color: #35495e; background: #f4f8ff; border-left: 4px solid #81a8d8;",
        "code_inline": "font-family: Menlo, Consolas, monospace; font-size: 0.92em; background: #f2f4f8; padding: 0.1em 0.34em; border-radius: 4px;",
        "pre": "margin: 1em 0; padding: 1em; background: #0b1f35; color: #eaf2ff; border-radius: 8px; overflow-x: auto; line-height: 1.6;",
        "hr": "border: none; border-top: 1px solid #d0d7de; margin: 1.2em 0;",
        "a": "color: #0969da; text-decoration: none; border-bottom: 1px solid #9cc1ea;",
        "strong": "font-weight: 700; color: #0f3b66;",
        "em": "font-style: italic; color: #2f5f8f;",
    },
    "tech": {
        "article": "max-width: 860px; margin: 0 auto; color: #0f172a; font-size: 16px; line-height: 1.8;",
        "h1": "font-size: 30px; line-height: 1.35; margin: 1.25em 0 0.68em; color: #111827;",
        "h2": "font-size: 24px; line-height: 1.4; margin: 1.2em 0 0.62em; color: #111827; border-bottom: 2px solid #0ea5e9; padding-bottom: 4px;",
        "h3": "font-size: 20px; line-height: 1.45; margin: 1.1em 0 0.52em; color: #0f172a;",
        "p": "margin: 0.82em 0;",
        "li": "margin: 0.32em 0;",
        "blockquote": "margin: 1em 0; padding: 0.8em 1em; color: #0f172a; background: #f8fafc; border-left: 4px solid #38bdf8;",
        "code_inline": "font-family: Menlo, Consolas, monospace; font-size: 0.92em; background: #eef2ff; color: #1e3a8a; padding: 0.1em 0.34em; border-radius: 4px;",
        "pre": "margin: 1em 0; padding: 1em; background: #0f172a; color: #dbeafe; border-radius: 8px; overflow-x: auto; line-height: 1.58;",
        "hr": "border: none; border-top: 1px solid #cbd5e1; margin: 1.15em 0;",
        "a": "color: #0369a1; text-decoration: none; border-bottom: 1px solid #7dd3fc;",
        "strong": "font-weight: 700; color: #1d4ed8;",
        "em": "font-style: italic; color: #0c4a6e;",
    },
    "warm": {
        "article": "max-width: 860px; margin: 0 auto; color: #3b2f2f; font-size: 16px; line-height: 1.82;",
        "h1": "font-size: 30px; line-height: 1.35; margin: 1.3em 0 0.7em; color: #5f2d1b;",
        "h2": "font-size: 24px; line-height: 1.42; margin: 1.2em 0 0.64em; color: #7a3118; border-left: 4px solid #d97706; padding-left: 10px;",
        "h3": "font-size: 20px; line-height: 1.46; margin: 1.1em 0 0.55em; color: #8a3d1f;",
        "p": "margin: 0.86em 0;",
        "li": "margin: 0.36em 0;",
        "blockquote": "margin: 1em 0; padding: 0.8em 1em; color: #5c4033; background: #fff8ef; border-left: 4px solid #f59e0b;",
        "code_inline": "font-family: Menlo, Consolas, monospace; font-size: 0.92em; background: #fff3e0; color: #7c2d12; padding: 0.1em 0.34em; border-radius: 4px;",
        "pre": "margin: 1em 0; padding: 1em; background: #402217; color: #fdecd6; border-radius: 8px; overflow-x: auto; line-height: 1.6;",
        "hr": "border: none; border-top: 1px solid #f3d3b0; margin: 1.2em 0;",
        "a": "color: #b45309; text-decoration: none; border-bottom: 1px solid #f2b874;",
        "strong": "font-weight: 700; color: #9a3412;",
        "em": "font-style: italic; color: #92400e;",
    },
    "apple": {
        "article": "max-width: 820px; margin: 0 auto; color: #1d1d1f; font-size: 17px; line-height: 1.82; letter-spacing: 0.01em;",
        "h1": "font-size: 34px; line-height: 1.28; margin: 1.35em 0 0.72em; color: #1d1d1f; font-weight: 700;",
        "h2": "font-size: 27px; line-height: 1.35; margin: 1.25em 0 0.66em; color: #1d1d1f; font-weight: 650;",
        "h3": "font-size: 22px; line-height: 1.42; margin: 1.15em 0 0.58em; color: #2c2c2e; font-weight: 600;",
        "p": "margin: 0.95em 0;",
        "li": "margin: 0.42em 0;",
        "blockquote": "margin: 1.05em 0; padding: 0.9em 1.05em; color: #3a3a3c; background: #f5f5f7; border-left: 3px solid #d2d2d7; border-radius: 8px;",
        "code_inline": "font-family: SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.91em; background: #f2f2f5; color: #1f1f22; padding: 0.1em 0.34em; border-radius: 5px;",
        "pre": "margin: 1.05em 0; padding: 1.02em; background: #1c1c1e; color: #f5f5f7; border-radius: 10px; overflow-x: auto; line-height: 1.6;",
        "hr": "border: none; border-top: 1px solid #e5e5ea; margin: 1.35em 0;",
        "a": "color: #0066cc; text-decoration: none;",
        "strong": "font-weight: 700; color: #1d1d1f;",
        "em": "font-style: italic; color: #3a3a3c;",
    },
    "wechat-native": {
        "article": "max-width: 680px; margin: 0 auto; width: 100%; box-sizing: border-box; background-color: #ffffff; border-radius: 12px; padding: 16px; color: #333333; font-size: 15px; line-height: 1.75; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;",
        "h1": "display: block; font-size: 29px; font-weight: 700; color: #163325; line-height: 1.32; margin: 36px 0 16px; letter-spacing: -0.015em; padding: 12px 16px 10px; background: linear-gradient(180deg, rgba(7,193,96,0.08) 0%, rgba(7,193,96,0.03) 100%); border-left: 5px solid #07c160; border-bottom: 1px dashed rgba(22,51,37,0.2); border-radius: 12px; box-shadow: 0 6px 14px rgba(7,193,96,0.05);",
        "h2": "display: block; font-size: 23px; font-weight: 700; color: #067647; line-height: 1.4; margin: 34px 0 18px; padding: 10px 14px; background: linear-gradient(90deg, rgba(7,193,96,0.12) 0%, rgba(7,193,96,0.03) 70%, rgba(7,193,96,0) 100%); border-left: 4px solid #07c160; border-radius: 12px;",
        "h3": "display: block; font-size: 20px; font-weight: 700; color: #0a6c44; line-height: 1.42; margin: 28px 0 14px; padding-left: 10px; border-left: 3px solid rgba(7,193,96,0.5);",
        "p": "margin: 18px 0; line-height: 1.75; color: #333333;",
        "li": "margin: 0.36em 0; color: #333333;",
        "blockquote": "margin: 1.1em 0; padding: 0.85em 1em; color: #214737; background: #f3fbf7; border-left: 4px solid #07c160; border-radius: 8px;",
        "code_inline": "font-family: 'SF Mono', Menlo, Consolas, monospace; padding: 3px 6px; background-color: #f0f7f2; color: #07c160; border-radius: 4px; font-size: 12px; line-height: 1.5;",
        "pre": "margin: 1.05em 0; padding: 1em; background: #0f2d1f; color: #ecfff4; border-radius: 8px; overflow-x: auto; line-height: 1.6;",
        "hr": "margin: 36px auto; border: none; height: 2px; width: 62%; background: linear-gradient(90deg, rgba(7,193,96,0) 0%, rgba(7,193,96,0.22) 20%, rgba(7,193,96,0.68) 50%, rgba(7,193,96,0.22) 80%, rgba(7,193,96,0) 100%);",
        "a": "color: #067647; text-decoration: none; border-bottom: 1px solid rgba(7,193,96,0.45);",
        "strong": "font-weight: 700; color: #067647; background: linear-gradient(180deg, rgba(7,193,96,0) 0%, rgba(7,193,96,0) 58%, rgba(7,193,96,0.16) 58%, rgba(7,193,96,0.16) 100%); padding: 0 3px;",
        "em": "font-style: italic; color: #666666;",
    },
}


def inline_format(text: str, theme: Dict[str, str]) -> str:
    placeholders: Dict[str, str] = {}

    def stash(val: str) -> str:
        key = f"@@P{len(placeholders)}@@"
        placeholders[key] = val
        return key

    escaped = escape(text)

    def repl_code(match: re.Match[str]) -> str:
        code = match.group(1)
        return stash(f"<code style=\"{theme['code_inline']}\">{escape(code)}</code>")

    escaped = re.sub(r"`([^`]+)`", repl_code, escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^\s)]+)\)",
        lambda m: f"<a href=\"{m.group(2)}\" style=\"{theme['a']}\">{m.group(1)}</a>",
        escaped,
    )
    escaped = re.sub(
        r"\*\*([^*]+)\*\*",
        lambda m: f"<strong style=\"{theme['strong']}\">{m.group(1)}</strong>",
        escaped,
    )
    escaped = re.sub(
        r"\*([^*]+)\*",
        lambda m: f"<em style=\"{theme['em']}\">{m.group(1)}</em>",
        escaped,
    )

    for key, val in placeholders.items():
        escaped = escaped.replace(key, val)

    return escaped


def parse_markdown(md: str, theme_name: str = "default", title: Optional[str] = None) -> str:
    theme = THEMES.get(theme_name, THEMES["default"])
    lines = md.replace("\r\n", "\n").split("\n")

    out: List[str] = []
    if title:
        out.append(f"<h1 style=\"{theme['h1']}\">{inline_format(title, theme)}</h1>")

    in_code = False
    code_lang = ""
    code_lines: List[str] = []

    list_type: Optional[str] = None
    list_items: List[str] = []

    paragraph_buffer: List[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph_buffer
        if paragraph_buffer:
            text = " ".join(part.strip() for part in paragraph_buffer).strip()
            if text:
                out.append(f"<p style=\"{theme['p']}\">{inline_format(text, theme)}</p>")
        paragraph_buffer = []

    def flush_list() -> None:
        nonlocal list_type, list_items
        if list_type and list_items:
            tag = "ul" if list_type == "ul" else "ol"
            rendered_items = "".join([f"<li style=\"{theme['li']}\">{item}</li>" for item in list_items])
            out.append(f"<{tag} style=\"margin: 0.6em 0 0.9em 1.2em; padding: 0;\">{rendered_items}</{tag}>")
        list_type = None
        list_items = []

    def flush_code() -> None:
        nonlocal in_code, code_lang, code_lines
        if in_code:
            lang_header = f"<div style=\"opacity: 0.75; margin-bottom: 0.55em;\">{escape(code_lang)}</div>" if code_lang else ""
            code_body = "\n".join(code_lines)
            out.append(
                f"<pre style=\"{theme['pre']}\">{lang_header}<code>{escape(code_body)}</code></pre>"
            )
        in_code = False
        code_lang = ""
        code_lines = []

    for raw in lines:
        line = raw.rstrip()

        code_fence = re.match(r"^```(.*)$", line)
        if code_fence:
            if in_code:
                flush_code()
            else:
                flush_paragraph()
                flush_list()
                in_code = True
                code_lang = code_fence.group(1).strip()
            continue

        if in_code:
            code_lines.append(raw)
            continue

        if re.match(r"^\s*$", line):
            flush_paragraph()
            flush_list()
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            text = heading.group(2).strip()
            style_map = {1: "h1", 2: "h2", 3: "h3", 4: "h3", 5: "h3", 6: "h3"}
            style_key = style_map[level]
            out.append(f"<h{level} style=\"{theme[style_key]}\">{inline_format(text, theme)}</h{level}>")
            continue

        if re.match(r"^(-{3,}|\*{3,})$", line.strip()):
            flush_paragraph()
            flush_list()
            out.append(f"<hr style=\"{theme['hr']}\" />")
            continue

        quote = re.match(r"^>\s?(.*)$", line)
        if quote:
            flush_paragraph()
            flush_list()
            out.append(f"<blockquote style=\"{theme['blockquote']}\">{inline_format(quote.group(1), theme)}</blockquote>")
            continue

        ul = re.match(r"^\s*[-*+]\s+(.+)$", line)
        if ul:
            flush_paragraph()
            if list_type not in (None, "ul"):
                flush_list()
            list_type = "ul"
            list_items.append(inline_format(ul.group(1), theme))
            continue

        ol = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if ol:
            flush_paragraph()
            if list_type not in (None, "ol"):
                flush_list()
            list_type = "ol"
            list_items.append(inline_format(ol.group(1), theme))
            continue

        paragraph_buffer.append(line)

    flush_paragraph()
    flush_list()
    if in_code:
        flush_code()

    body = "\n".join(out)
    return f"<article style=\"{theme['article']}\">\n{body}\n</article>"


def copy_html_to_macos_clipboard(html: str) -> None:
    if sys.platform != "darwin":
        raise RuntimeError("Clipboard copy is only supported on macOS.")
    if shutil.which("osascript") is None:
        raise RuntimeError("osascript not found; cannot write rich HTML to clipboard.")

    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".html", delete=False) as tmp:
        tmp.write(html)
        tmp_path = tmp.name

    try:
        script = f"""
set f to POSIX file "{tmp_path}"
set the clipboard to (read f as «class HTML»)
"""
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def ensure_cache_dir(cwd: Optional[str] = None) -> str:
    base_dir = cwd or os.getcwd()
    candidates = [
        os.getenv("WECHAT_MCP_CACHE_DIR"),
        os.path.join(base_dir, ".cache", "wechat-mcp"),
        os.path.join(os.getcwd(), ".cache", "wechat-mcp"),
        os.path.join(os.path.abspath(os.path.expanduser(os.getenv("XDG_CACHE_HOME", ""))), "wechat-mcp")
        if os.getenv("XDG_CACHE_HOME")
        else None,
        os.path.join(os.path.expanduser("~"), "Library", "Caches", "wechat-mcp")
        if sys.platform == "darwin"
        else os.path.join(os.path.expanduser("~"), ".cache", "wechat-mcp"),
        os.path.join(tempfile.gettempdir(), "wechat-mcp"),
    ]
    for raw in candidates:
        if not raw:
            continue
        candidate = os.path.abspath(os.path.expanduser(raw))
        try:
            os.makedirs(candidate, exist_ok=True)
            return candidate
        except OSError:
            continue
    raise RuntimeError("Failed to create cache directory.")


def save_html_cache(html: str, cwd: Optional[str] = None, cache_dir: Optional[str] = None) -> str:
    final_dir = cache_dir or ensure_cache_dir(cwd=cwd)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_path = os.path.join(final_dir, f"wechat-{stamp}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    return file_path


class MCPServer:
    def __init__(self) -> None:
        self.initialized = False
        self.shutdown_requested = False

    def read_message(self) -> Optional[Dict[str, Any]]:
        while True:
            headers: Dict[str, str] = {}
            while True:
                line = sys.stdin.buffer.readline()
                if not line:
                    return None
                stripped = line.strip()
                if not stripped:
                    break
                try:
                    decoded = stripped.decode("utf-8", errors="replace")
                except Exception:  # noqa: BLE001
                    continue
                if ":" in decoded:
                    key, value = decoded.split(":", 1)
                    headers[key.strip().lower()] = value.strip()

            length_raw = headers.get("content-length")
            if not length_raw:
                continue

            try:
                length = int(length_raw)
            except ValueError:
                self.send_error(None, -32700, f"Invalid Content-Length: {length_raw}")
                continue

            content = sys.stdin.buffer.read(length)
            if not content:
                return None

            try:
                return json.loads(content.decode("utf-8"))
            except json.JSONDecodeError as e:
                self.send_error(None, -32700, f"Invalid JSON payload: {e}")
                continue

    def send(self, payload: Dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        header = f"Content-Length: {len(data)}\r\n\r\n".encode("utf-8")
        sys.stdout.buffer.write(header)
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()

    def send_response(self, req_id: Any, result: Dict[str, Any]) -> None:
        self.send({"jsonrpc": "2.0", "id": req_id, "result": result})

    def send_error(self, req_id: Any, code: int, message: str) -> None:
        self.send({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})

    def handle_initialize(self, req_id: Any) -> None:
        self.initialized = True
        self.send_response(
            req_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "serverInfo": {"name": "wechat-markdown-mcp", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        )

    def handle_tools_list(self, req_id: Any) -> None:
        self.send_response(
            req_id,
            {
                "tools": [
                    {
                        "name": "convert_markdown_to_wechat_html",
                        "description": "Convert Markdown to WeChat-friendly HTML with inline styles for copy/paste publishing workflows.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "markdown": {
                                    "type": "string",
                                    "description": "Source markdown text",
                                },
                                "theme": {
                                    "type": "string",
                                    "description": "Theme name: default | tech | warm | apple | wechat-native",
                                    "enum": ["default", "tech", "warm", "apple", "wechat-native"],
                                    "default": "default",
                                },
                                "title": {
                                    "type": "string",
                                    "description": "Optional article title rendered as h1",
                                },
                            },
                            "required": ["markdown"],
                        },
                    },
                    {
                        "name": "list_wechat_themes",
                        "description": "List available rendering themes.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                        },
                    },
                    {
                        "name": "convert_markdown_to_wechat_clipboard",
                        "description": "Convert Markdown to WeChat-friendly HTML and copy as rich HTML to macOS clipboard.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "markdown": {
                                    "type": "string",
                                    "description": "Source markdown text",
                                },
                                "theme": {
                                    "type": "string",
                                    "description": "Theme name: default | tech | warm | apple | wechat-native",
                                    "enum": ["default", "tech", "warm", "apple", "wechat-native"],
                                    "default": "default",
                                },
                                "title": {
                                    "type": "string",
                                    "description": "Optional article title rendered as h1",
                                },
                            },
                            "required": ["markdown"],
                        },
                    },
                ]
            },
        )

    def handle_tools_call(self, req_id: Any, params: Dict[str, Any]) -> None:
        name = params.get("name")
        arguments = params.get("arguments", {})

        if name == "list_wechat_themes":
            self.send_response(
                req_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "themes": [
                                        {
                                            "name": "default",
                                            "description": "Balanced enterprise style",
                                        },
                                        {
                                            "name": "tech",
                                            "description": "Clean technical publication style",
                                        },
                                        {
                                            "name": "warm",
                                            "description": "Warmer brand/media style",
                                        },
                                        {
                                            "name": "apple",
                                            "description": "Apple-like minimalist editorial style",
                                        },
                                        {
                                            "name": "wechat-native",
                                            "description": "WeChat native-like green visual style",
                                        },
                                    ]
                                },
                                ensure_ascii=False,
                                indent=2,
                            ),
                        }
                    ]
                },
            )
            return

        if name == "convert_markdown_to_wechat_html":
            markdown = arguments.get("markdown")
            if not isinstance(markdown, str) or markdown.strip() == "":
                self.send_response(
                    req_id,
                    {
                        "content": [{"type": "text", "text": "markdown is required and must be a non-empty string."}],
                        "isError": True,
                    },
                )
                return

            theme = arguments.get("theme", "default")
            if not isinstance(theme, str) or theme not in THEMES:
                self.send_response(
                    req_id,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Invalid theme: {theme}. Available: {', '.join(sorted(THEMES.keys()))}",
                            }
                        ],
                        "isError": True,
                    },
                )
                return
            title = arguments.get("title")
            html = parse_markdown(markdown, theme_name=theme, title=title)
            saved_path = save_html_cache(html)
            self.send_response(
                req_id,
                {
                    "content": [{"type": "text", "text": html}],
                    "meta": {"cacheHtmlPath": saved_path},
                },
            )
            return

        if name == "convert_markdown_to_wechat_clipboard":
            markdown = arguments.get("markdown")
            if not isinstance(markdown, str) or markdown.strip() == "":
                self.send_response(
                    req_id,
                    {
                        "content": [{"type": "text", "text": "markdown is required and must be a non-empty string."}],
                        "isError": True,
                    },
                )
                return

            theme = arguments.get("theme", "default")
            if not isinstance(theme, str) or theme not in THEMES:
                self.send_response(
                    req_id,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Invalid theme: {theme}. Available: {', '.join(sorted(THEMES.keys()))}",
                            }
                        ],
                        "isError": True,
                    },
                )
                return
            title = arguments.get("title")
            html = parse_markdown(markdown, theme_name=theme, title=title)
            saved_path = save_html_cache(html)
            try:
                copy_html_to_macos_clipboard(html)
            except Exception as e:  # noqa: BLE001
                self.send_response(
                    req_id,
                    {
                        "content": [{"type": "text", "text": f"Clipboard copy failed: {e}"}],
                        "isError": True,
                    },
                )
                return

            self.send_response(
                req_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "ok": True,
                                    "message": "Copied as HTML rich text to macOS clipboard.",
                                    "htmlLength": len(html),
                                    "theme": theme,
                                    "cacheHtmlPath": saved_path,
                                },
                                ensure_ascii=False,
                            ),
                        }
                    ]
                },
            )
            return

        self.send_response(
            req_id,
            {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True},
        )

    def serve_forever(self) -> None:
        while True:
            msg = self.read_message()
            if msg is None:
                break

            method = msg.get("method")
            req_id = msg.get("id")
            params = msg.get("params", {})

            if method == "initialize":
                self.handle_initialize(req_id)
                continue

            if method == "notifications/initialized":
                continue

            if method == "shutdown":
                self.shutdown_requested = True
                if req_id is not None:
                    self.send_response(req_id, {})
                continue

            if method == "exit":
                break

            if method == "tools/list":
                self.handle_tools_list(req_id)
                continue

            if method == "tools/call":
                self.handle_tools_call(req_id, params)
                continue

            if method == "ping":
                self.send_response(req_id, {})
                continue

            if req_id is not None:
                self.send_error(req_id, -32601, f"Method not found: {method}")


def main() -> None:
    server = MCPServer()
    server.serve_forever()


if __name__ == "__main__":
    main()

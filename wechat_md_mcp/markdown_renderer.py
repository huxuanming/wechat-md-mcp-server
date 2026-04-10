import re
from html import escape
from typing import Dict, List, Optional

from .themes import THEMES


def inline_format(text: str, theme: Dict[str, str]) -> str:
    placeholders: Dict[str, str] = {}

    def stash(val: str) -> str:
        key = f"@@P{len(placeholders)}@@"
        placeholders[key] = val
        return key

    escaped = escape(text)

    def repl_code(match: re.Match) -> str:
        code = match.group(1)
        return stash(f"<code style=\"{theme['code_inline']}\">{code}</code>")

    escaped = re.sub(r"`([^`]+)`", repl_code, escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\(((?:https?://|ftp://|mailto:|#)[^\s)]*)\)",
        lambda m: f"<a href=\"{m.group(2)}\" style=\"{theme['a']}\">{m.group(1)}</a>",
        escaped,
    )
    escaped = re.sub(
        r"\*\*(.+?)\*\*",
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
            out.append(f"<pre style=\"{theme['pre']}\">{lang_header}<code>{escape(code_body)}</code></pre>")
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

        flush_list()
        paragraph_buffer.append(line)

    flush_paragraph()
    flush_list()
    if in_code:
        flush_code()

    body = "\n".join(out)
    return f"<article style=\"{theme['article']}\">\n{body}\n</article>"

#!/usr/bin/env python3
import argparse
from pathlib import Path

import wechat_mcp_server as w


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert Markdown to WeChat HTML, optionally copy as rich HTML clipboard."
    )
    parser.add_argument("input", help="Input markdown file path")
    parser.add_argument(
        "--theme",
        choices=["default", "tech", "warm", "apple", "wechat-native"],
        default="default",
        help="Rendering theme",
    )
    parser.add_argument("--title", default=None, help="Optional title override")
    parser.add_argument(
        "--out",
        default=None,
        help="Optional output html path; if omitted, use .cache/wechat-mcp",
    )
    parser.add_argument(
        "--cache-dir",
        default=None,
        help="Override cache directory (or set WECHAT_MCP_CACHE_DIR).",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy HTML to macOS clipboard as rich HTML",
    )

    args = parser.parse_args()

    md_path = Path(args.input).expanduser().resolve()
    if not md_path.exists() or not md_path.is_file():
        raise SystemExit(f"Input file not found: {md_path}")

    markdown = md_path.read_text(encoding="utf-8")
    html = w.parse_markdown(markdown, theme_name=args.theme, title=args.title)

    if args.out:
        out_path = Path(args.out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
    else:
        out_path = Path(w.save_html_cache(html, cwd=str(md_path.parent), cache_dir=args.cache_dir))

    copied = False
    if args.copy:
        w.copy_html_to_macos_clipboard(html)
        copied = True

    print(f"Input: {md_path}")
    print(f"Theme: {args.theme}")
    print(f"Output: {out_path}")
    print(f"Clipboard: {'yes' if copied else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

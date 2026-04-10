#!/usr/bin/env python3
import argparse
from pathlib import Path

from wechat_md_mcp import parse_markdown, save_html_cache


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert Markdown to WeChat HTML."
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
        "--open",
        action="store_true",
        help="Open output HTML in browser after conversion",
    )

    args = parser.parse_args()

    md_path = Path(args.input).expanduser().resolve()
    if not md_path.exists() or not md_path.is_file():
        raise SystemExit(f"Input file not found: {md_path}")

    markdown = md_path.read_text(encoding="utf-8")
    html = parse_markdown(markdown, theme_name=args.theme, title=args.title)

    if args.out:
        out_path = Path(args.out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
    else:
        try:
            out_path = Path(save_html_cache(html, cache_dir=args.cache_dir))
        except Exception as e:
            raise SystemExit(f"Failed to save cache: {e}")

    print(f"Input: {md_path}")
    print(f"Theme: {args.theme}")
    print(f"Output: {out_path}")

    if args.open:
        import webbrowser
        webbrowser.open(out_path.resolve().as_uri())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import os
from datetime import datetime
from typing import Optional


def ensure_cache_dir(cache_dir: Optional[str] = None) -> str:
    raw = cache_dir or os.getenv("WECHAT_MCP_CACHE_DIR") or os.path.join(os.getcwd(), ".cache", "wechat-mcp")
    path = os.path.abspath(os.path.expanduser(raw))
    os.makedirs(path, exist_ok=True)
    return path


def save_html_cache(html: str, cache_dir: Optional[str] = None) -> str:
    final_dir = ensure_cache_dir(cache_dir=cache_dir)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    file_path = os.path.join(final_dir, f"wechat-{stamp}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    return file_path

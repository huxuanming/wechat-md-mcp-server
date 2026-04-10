import asyncio
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import server as s  # noqa: E402


class TestToolValidation(unittest.TestCase):
    def test_convert_markdown_rejects_non_string_title(self) -> None:
        with self.assertRaises(ValueError):
            asyncio.run(
                s.call_tool(
                    "convert_markdown_to_wechat_html",
                    {"markdown": "hello", "title": 123},
                )
            )


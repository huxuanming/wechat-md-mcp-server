import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import server as s  # noqa: E402


class TestParseMarkdown(unittest.TestCase):
    def test_empty_input(self) -> None:
        html = s.parse_markdown("")
        self.assertIn("<article", html)
        self.assertIn("</article>", html)

    def test_heading_h1(self) -> None:
        html = s.parse_markdown("# Hello")
        self.assertIn("<h1", html)
        self.assertIn("Hello", html)

    def test_heading_h2(self) -> None:
        html = s.parse_markdown("## Section")
        self.assertIn("<h2", html)

    def test_heading_h3(self) -> None:
        html = s.parse_markdown("### Sub")
        self.assertIn("<h3", html)

    def test_paragraph(self) -> None:
        html = s.parse_markdown("Hello world")
        self.assertIn("<p", html)
        self.assertIn("Hello world", html)

    def test_bold(self) -> None:
        html = s.parse_markdown("**bold text**")
        self.assertIn("<strong", html)
        self.assertIn("bold text", html)

    def test_italic(self) -> None:
        html = s.parse_markdown("*italic text*")
        self.assertIn("<em", html)
        self.assertIn("italic text", html)

    def test_bold_containing_italic(self) -> None:
        html = s.parse_markdown("**bold *italic* bold**")
        self.assertIn("<strong", html)

    def test_inline_code(self) -> None:
        html = s.parse_markdown("`print('hi')`")
        self.assertIn("<code", html)
        self.assertIn("print", html)

    def test_fenced_code_block(self) -> None:
        html = s.parse_markdown("```python\nprint('hi')\n```")
        self.assertIn("<pre", html)
        self.assertIn("<code>", html)
        self.assertIn("print", html)

    def test_cache_path_returned(self) -> None:
        os.environ["WECHAT_MCP_CACHE_DIR"] = tempfile.mkdtemp()
        result = s.save_html_cache("<article>test</article>")
        self.assertTrue(Path(result).is_file())

    def test_http_link(self) -> None:
        html = s.parse_markdown("[click](https://example.com)")
        self.assertIn('href="https://example.com"', html)
        self.assertIn("click", html)

    def test_anchor_link(self) -> None:
        html = s.parse_markdown("[jump](#section)")
        self.assertIn('href="#section"', html)

    def test_mailto_link(self) -> None:
        html = s.parse_markdown("[email](mailto:foo@bar.com)")
        self.assertIn('href="mailto:foo@bar.com"', html)

    def test_blockquote(self) -> None:
        html = s.parse_markdown("> quoted text")
        self.assertIn("<blockquote", html)
        self.assertIn("quoted text", html)

    def test_unordered_list(self) -> None:
        html = s.parse_markdown("- item1\n- item2")
        self.assertIn("<ul", html)
        self.assertIn("<li", html)
        self.assertIn("item1", html)

    def test_ordered_list(self) -> None:
        html = s.parse_markdown("1. first\n2. second")
        self.assertIn("<ol", html)
        self.assertIn("first", html)

    def test_horizontal_rule(self) -> None:
        html = s.parse_markdown("---")
        self.assertIn("<hr", html)

    def test_title_option(self) -> None:
        html = s.parse_markdown("content", title="My Title")
        self.assertIn("<h1", html)
        self.assertIn("My Title", html)

    def test_all_themes(self) -> None:
        for theme in ("default", "tech", "warm", "apple", "wechat-native"):
            with self.subTest(theme=theme):
                html = s.parse_markdown("# Hello\n\nParagraph.", theme_name=theme)
                self.assertIn("<article", html)
                self.assertIn("<h1", html)

    def test_html_special_chars_escaped(self) -> None:
        html = s.parse_markdown("a < b & c > d")
        self.assertIn("&lt;", html)
        self.assertIn("&amp;", html)
        self.assertIn("&gt;", html)

    def test_unclosed_code_block(self) -> None:
        html = s.parse_markdown("```python\nprint('hi')")
        self.assertIn("<pre", html)

    def test_multiline_paragraph(self) -> None:
        html = s.parse_markdown("line one\nline two")
        self.assertIn("<p", html)


class TestInlineFormat(unittest.TestCase):
    def _fmt(self, text: str) -> str:
        return s.inline_format(text, s.THEMES["default"])

    def test_bold(self) -> None:
        self.assertIn("<strong", self._fmt("**bold**"))

    def test_italic(self) -> None:
        self.assertIn("<em", self._fmt("*italic*"))

    def test_inline_code(self) -> None:
        self.assertIn("<code", self._fmt("`code`"))

    def test_link(self) -> None:
        result = self._fmt("[text](https://example.com)")
        self.assertIn("href=", result)

    def test_plain_text(self) -> None:
        result = self._fmt("hello world")
        self.assertEqual(result, "hello world")

    def test_html_entities_escaped(self) -> None:
        result = self._fmt("<script>")
        self.assertNotIn("<script>", result)
        self.assertIn("&lt;", result)


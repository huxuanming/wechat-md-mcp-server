import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestCliHelp(unittest.TestCase):
    def test_help_flag_shows_usage(self) -> None:
        proc = subprocess.run(
            ["uvx", "--from", str(ROOT), "wechat-md-mcp-server", "-h"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("usage:", proc.stdout.lower())
        self.assertIn("wechat-md-mcp-server", proc.stdout)

    def test_version_flag(self) -> None:
        proc = subprocess.run(
            ["uvx", "--from", str(ROOT), "wechat-md-mcp-server", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("0.2.0", proc.stdout)


if __name__ == "__main__":
    unittest.main()

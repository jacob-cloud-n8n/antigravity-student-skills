from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
INIT_SCRIPT = SKILL_ROOT / "scripts" / "init_workspace.py"
AUDIT_SCRIPT = SKILL_ROOT / "scripts" / "audit_workspace.py"


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


class WorkspaceToolsTest(unittest.TestCase):
    def test_dry_run_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            result = run_script(INIT_SCRIPT, str(base))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("預覽（尚未寫入）", result.stdout)
            self.assertFalse((base / "AI協作系統").exists())

    def test_apply_creates_complete_workspace_and_audit_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            init_result = run_script(INIT_SCRIPT, str(base), "--apply")
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            system_dir = base / "AI協作系統"
            self.assertTrue((system_dir / "profile" / "我的AI協作檔案.md").is_file())
            self.assertTrue((system_dir / "adapters" / "codex.md").is_file())

            audit_result = run_script(AUDIT_SCRIPT, str(base))
            self.assertEqual(audit_result.returncode, 0, audit_result.stdout)
            self.assertIn("結果：PASS", audit_result.stdout)

    def test_reapply_never_overwrites_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            self.assertEqual(run_script(INIT_SCRIPT, str(base), "--apply").returncode, 0)
            profile = base / "AI協作系統" / "profile" / "我的AI協作檔案.md"
            profile.write_text("學員已校正的內容\n", encoding="utf-8")

            result = run_script(INIT_SCRIPT, str(base), "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(profile.read_text(encoding="utf-8"), "學員已校正的內容\n")
            self.assertIn("保留既有：9 個檔案", result.stdout)

    def test_audit_fails_on_machine_specific_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            self.assertEqual(run_script(INIT_SCRIPT, str(base), "--apply").returncode, 0)
            profile = base / "AI協作系統" / "profile" / "我的AI協作檔案.md"
            profile.write_text("資料在 /Users/example/Desktop/work.md\n", encoding="utf-8")

            result = run_script(AUDIT_SCRIPT, str(base))
            self.assertEqual(result.returncode, 1)
            self.assertIn("機器專屬絕對路徑", result.stdout)

    def test_audit_fails_on_secret_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            self.assertEqual(run_script(INIT_SCRIPT, str(base), "--apply").returncode, 0)
            profile = base / "AI協作系統" / "profile" / "我的AI協作檔案.md"
            simulated_secret = "sk-" + ("A" * 24)
            profile.write_text(f"不應保存：{simulated_secret}\n", encoding="utf-8")

            result = run_script(AUDIT_SCRIPT, str(base))
            self.assertEqual(result.returncode, 1)
            self.assertIn("疑似秘密值", result.stdout)


if __name__ == "__main__":
    unittest.main()

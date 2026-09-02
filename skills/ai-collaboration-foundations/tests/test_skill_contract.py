from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (SKILL_ROOT / relative).read_text(encoding="utf-8")


class SkillContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = read("SKILL.md")
        cls.interview = read("references/guided-interview.md")
        cls.import_guide = read("references/prior-ai-import.md")
        cls.workspace = read("references/workspace-contract.md")
        cls.work_cycle = read("references/work-cycle.md")

    def test_new_learner_route_is_guided_and_work_focused(self) -> None:
        self.assertIn("第一次建立", self.skill)
        self.assertIn("第一項真實工作", self.skill)
        self.assertIn("八個核心問題", self.interview)
        self.assertIn("一次問一題", self.interview)
        self.assertIn("同一主題最多三輪", self.interview)
        self.assertIn("不需要填詳細身分", read("assets/workspace-template/profile/我的AI協作檔案.md"))

    def test_existing_student_route_preserves_current_foundations(self) -> None:
        self.assertIn("已有開工／第二大腦", self.skill)
        self.assertIn("不得重新初始化或搬動二腦", self.skill)
        self.assertIn("不移動第二大腦、不重建 Git", self.workspace)
        self.assertIn("只登記位置，不搬動、不複製", read("assets/workspace-template/index.md"))

    def test_prior_ai_route_separates_content_from_platform_capabilities(self) -> None:
        self.assertIn("六步匯入精靈", self.import_guide)
        self.assertIn("instruction-only", self.import_guide)
        self.assertIn("需另接", self.import_guide)
        self.assertIn("gpt-role-to-codex-skill", self.import_guide)
        self.assertIn("逐項連接與實測", self.import_guide)

    def test_work_cycle_requires_confirmation_and_second_task(self) -> None:
        self.assertIn("需求 → 釐清 → 計畫", self.skill)
        self.assertIn("新增／修改正式檔案", self.work_cycle)
        self.assertIn("先預覽並確認", self.work_cycle)
        self.assertIn("第二項任務", self.work_cycle)

    def test_portability_contract_is_explicit(self) -> None:
        for statement in ("資料可攜", "平台可替換", "接線可重建", "核心內容不重做"):
            self.assertIn(statement, self.workspace)
        self.assertIn("相對路徑", self.workspace)
        self.assertIn("真實工作驗證", self.workspace)


if __name__ == "__main__":
    unittest.main()

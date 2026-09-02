#!/usr/bin/env python3
"""Read-only portability and secret-pattern audit for an AI collaboration workspace."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SYSTEM_DIR_NAME = "AI協作系統"
REQUIRED_FILES = (
    "index.md",
    "profile/我的AI協作檔案.md",
    "projects/README.md",
    "templates/工作協作卡.md",
    "templates/專案協作模板.md",
    "templates/收工紀錄模板.md",
    "adapters/codex.md",
    "adapters/claude.md",
    "adapters/gemini.md",
)
SECRET_PATTERNS = (
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("openai-style-token", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("google-api-key", re.compile(r"\bAIza[A-Za-z0-9_-]{30,}\b")),
    ("aws-access-key", re.compile(r"\bAKIA[A-Z0-9]{16}\b")),
    # 下面三條補的是「前綴樣式表」天生的盲區：不是每一種憑證都有可辨識的前綴。
    # 血證 2026-09-01：Telegram bot token 明文躺在版控 27 天，六家族樣式表全部沒中。
    ("telegram-bot-token", re.compile(
        r"(?<![0-9])[0-9]{8,10}:[A-Za-z0-9_-]{35}(?![A-Za-z0-9_-])")),
    ("discord-bot-token", re.compile(
        r"\b[MNO][A-Za-z0-9_-]{23,}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27,}\b")),
    # 兜底：關鍵字後面直接接一段長值。占位符（<...>、待填、環境變數名）不算。
    ("keyword-assigned-secret", re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|bot[_-]?token"
        r"|secret|password|passwd|private[_-]?key)\b"
        r"\s*[:=]\s*(?![<`'\"]|待填|待補|環境變數|\$\{?[A-Z_]+)[^\s]{16,}")),
)
ABSOLUTE_PATH_PATTERNS = (
    re.compile(r"(?<![A-Za-z0-9_])/Users/[^\s)`>]+"),
    re.compile(r"(?<![A-Za-z0-9_])/home/[^\s)`>]+"),
    re.compile(r"\b[A-Za-z]:\\Users\\[^\s)`>]+"),
)


def resolve_system_dir(path: Path) -> Path:
    path = path.expanduser().resolve()
    return path if path.name == SYSTEM_DIR_NAME else path / SYSTEM_DIR_NAME


def audit(path: Path) -> dict[str, object]:
    root = resolve_system_dir(path)
    errors: list[str] = []
    warnings: list[str] = []

    if not root.is_dir():
        return {"root": str(root), "errors": ["找不到 AI協作系統 資料夾"], "warnings": []}

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"缺少必要檔案：{relative}")

    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file():
            continue
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = file_path.relative_to(root)
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(content):
                errors.append(f"疑似秘密值：{relative} ({label})")
        for pattern in ABSOLUTE_PATH_PATTERNS:
            if pattern.search(content):
                errors.append(f"機器專屬絕對路徑：{relative}")
                break

    profile = root / "profile" / "我的AI協作檔案.md"
    if profile.is_file() and profile.read_text(encoding="utf-8").count("待訪談") >= 5:
        warnings.append("協作檔案仍多為待訪談欄位；先完成工作導向採訪再進行真實任務。")

    index = root / "index.md"
    if index.is_file() and "<相對路徑或尚未啟用>" in index.read_text(encoding="utf-8"):
        warnings.append("第二大腦尚未登記；若已有二腦，請只填相對路徑，不要搬動內容。")

    return {"root": str(root), "errors": errors, "warnings": warnings}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="唯讀檢查 AI 協作系統的完整性、可攜性與秘密值樣式。")
    parser.add_argument("path", type=Path, help="工作資料夾或 AI協作系統 路徑")
    parser.add_argument("--json", action="store_true", help="輸出 JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = audit(args.path)
    errors = result["errors"]
    warnings = result["warnings"]

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"檢查目標：{result['root']}")
        if errors:
            print("錯誤：")
            for item in errors:
                print(f"  - {item}")
        else:
            print("錯誤：0")
        if warnings:
            print("提醒：")
            for item in warnings:
                print(f"  - {item}")
        else:
            print("提醒：0")
        print("結果：FAIL" if errors else "結果：PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

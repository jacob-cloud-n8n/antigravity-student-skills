#!/usr/bin/env python3
"""Preview or safely initialize a learner's portable AI collaboration workspace."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


SYSTEM_DIR_NAME = "AI協作系統"
SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "workspace-template"


def resolve_target(destination: Path) -> Path:
    destination = destination.expanduser().resolve()
    return destination if destination.name == SYSTEM_DIR_NAME else destination / SYSTEM_DIR_NAME


def template_files() -> list[Path]:
    if not TEMPLATE_ROOT.is_dir():
        raise FileNotFoundError(f"找不到模板目錄：{TEMPLATE_ROOT}")
    return sorted(path for path in TEMPLATE_ROOT.rglob("*") if path.is_file())


def initialize(destination: Path, apply: bool = False) -> tuple[Path, list[Path], list[Path]]:
    target = resolve_target(destination)
    if target.exists() and not target.is_dir():
        raise NotADirectoryError(f"目標已存在且不是資料夾：{target}")

    created: list[Path] = []
    skipped: list[Path] = []
    for source in template_files():
        relative = source.relative_to(TEMPLATE_ROOT)
        output = target / relative
        if output.exists():
            skipped.append(relative)
            continue
        created.append(relative)
        if apply:
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, output)
    return target, created, skipped


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="預覽或建立可攜的 AI 協作系統；預設不寫入。"
    )
    parser.add_argument("destination", type=Path, help="學員選定的工作資料夾，或既有 AI協作系統 路徑")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="實際建立缺少的檔案；既有檔案永不覆蓋",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        target, created, skipped = initialize(args.destination, apply=args.apply)
    except (FileNotFoundError, NotADirectoryError, OSError) as error:
        print(f"錯誤：{error}", file=sys.stderr)
        return 2

    mode = "已建立" if args.apply else "預覽（尚未寫入）"
    print(f"模式：{mode}")
    print(f"目標：{target}")
    print(f"將新增／已新增：{len(created)} 個檔案")
    for relative in created:
        print(f"  + {relative}")
    print(f"保留既有：{len(skipped)} 個檔案")
    for relative in skipped:
        print(f"  = {relative}")

    if not args.apply:
        print("下一步：向學員顯示本預覽；確認後再使用 --apply。")
    elif created:
        print("下一步：訪談並預覽 profile/我的AI協作檔案.md 的草稿，確認後再更新。")
    else:
        print("下一步：現有檔案均已保留；先唯讀盤點再提出補強草稿。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

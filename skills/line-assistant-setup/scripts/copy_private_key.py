#!/usr/bin/env python3
"""把 Google 服務帳戶 JSON 裡的私鑰，以正確換行格式放進 macOS 剪貼簿。

用法：python3 copy_private_key.py <服務帳戶金鑰.json>
畫面只顯示檔名與格式檢查結果，不顯示金鑰內容。
"""
import json
import os
import subprocess
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("用法：python3 copy_private_key.py <服務帳戶金鑰.json>")
        return 1
    path = os.path.expanduser(sys.argv[1])
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"讀不到這個 JSON：{e.__class__.__name__}")
        return 1
    key = data.get("private_key", "")
    pem_head = "-----BEGIN " + "PRIVATE KEY-----"
    if not key.startswith(pem_head):
        print("這個檔案裡沒有正確的 private_key，確認下載的是服務帳戶的 JSON 金鑰。")
        return 1
    # Windows 用系統 clip（未實測），其他用 macOS pbcopy
    clip_cmd = "clip" if sys.platform.startswith("win") else "pbcopy"
    subprocess.run(clip_cmd, input=key.encode(), check=True)
    print(f"已複製私鑰（來源：{os.path.basename(path)}），格式 OK。")
    print("貼進 n8n 後請清空剪貼簿，並把這個 JSON 丟到垃圾桶。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

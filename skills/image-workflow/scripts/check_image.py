#!/usr/bin/env python3
"""Read-only image decoding, dimension, aspect and alpha checks; JSON result."""

import argparse
import json
import sys
from pathlib import Path


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("尺寸必須是正整數")
    return number


def aspect_ratio(value):
    try:
        left, right = value.split(":")
        width, height = float(left), float(right)
        if not (0 < width < float("inf") and 0 < height < float("inf")):
            raise ValueError
        return width / height
    except (ValueError, ZeroDivisionError):
        raise argparse.ArgumentTypeError("比例格式需為正數 W:H，例如 4:5") from None


def emit(result):
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--require-transparent", action="store_true")
    parser.add_argument("--min-width", type=positive_int)
    parser.add_argument("--min-height", type=positive_int)
    parser.add_argument("--aspect", type=aspect_ratio, help="W:H，允許 1%% 相對誤差")
    args = parser.parse_args()
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError:
        emit({"ok": False, "error": "missing-pillow", "message": "檔案檢查需要 Pillow；可先使用既有影像工具，生圖本身不需此套件。"})
        return 2

    result = {"ok": False, "file": str(args.image), "failures": []}
    try:
        with Image.open(args.image) as image:
            image.load()
            width, height = image.size
            alpha_min, alpha_max = image.convert("RGBA").getchannel("A").getextrema()
            result.update({"decoded": True, "format": image.format, "mode": image.mode,
                           "width": width, "height": height,
                           "alpha_min": alpha_min, "alpha_max": alpha_max,
                           "has_transparent_pixels": alpha_min < 255,
                           "has_visible_pixels": alpha_max > 0})
            if args.min_width and width < args.min_width:
                result["failures"].append("width-below-minimum")
            if args.min_height and height < args.min_height:
                result["failures"].append("height-below-minimum")
            if args.aspect and abs((width / height) / args.aspect - 1) > 0.01:
                result["failures"].append("aspect-mismatch")
            if alpha_max == 0:
                result["failures"].append("fully-transparent-empty-image")
            if args.require_transparent and alpha_min == 255:
                result["failures"].append("no-transparent-pixels")
            if args.require_transparent and image.format not in {"PNG", "WEBP"}:
                result["failures"].append("unsupported-transparent-delivery-format")
    except FileNotFoundError:
        result.update({"decoded": False, "error": "file-not-found"})
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        result.update({"decoded": False, "error": "image-cannot-be-decoded"})
    result["ok"] = result.get("decoded", False) and not result["failures"]
    emit(result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

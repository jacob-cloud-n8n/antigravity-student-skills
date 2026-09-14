#!/usr/bin/env python3
"""Verify observable CLI behavior with temporary images; no network or editing."""

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image


def main():
    checker = Path(__file__).with_name("check_image.py")
    with tempfile.TemporaryDirectory(prefix="image-workflow-checks-") as folder:
        root = Path(folder)
        rgba = Image.new("RGBA", (40, 50), (20, 70, 160, 0))
        rgba.paste((20, 70, 160, 255), (10, 10, 30, 40))
        rgba.save(root / "transparent.png")
        rgba.save(root / "transparent.webp", lossless=True)
        Image.new("RGBA", (40, 50), (20, 70, 160, 255)).save(root / "opaque-rgba.png")
        Image.new("RGB", (40, 50), "gray").save(root / "opaque.jpg")
        Image.new("RGBA", (40, 50), (0, 0, 0, 0)).save(root / "empty.png")
        palette = Image.new("P", (40, 50), 0)
        palette.putpalette([0, 0, 0, 30, 80, 140] + [0] * 762)
        palette.paste(1, (10, 10, 30, 40))
        palette.save(root / "palette.png", transparency=0)
        (root / "corrupt.png").write_bytes(b"not an image")
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}
        cases = [
            ("transparent.png", ["--require-transparent", "--aspect", "4:5"], 0, None),
            ("transparent.webp", ["--require-transparent"], 0, None),
            ("palette.png", ["--require-transparent"], 0, None),
            ("opaque-rgba.png", [], 0, None),
            ("opaque-rgba.png", ["--require-transparent"], 1, "no-transparent-pixels"),
            ("opaque.jpg", ["--require-transparent"], 1, "no-transparent-pixels"),
            ("empty.png", ["--require-transparent"], 1, "fully-transparent-empty-image"),
            ("transparent.png", ["--min-width", "41"], 1, "width-below-minimum"),
            ("transparent.png", ["--min-height", "51"], 1, "height-below-minimum"),
            ("transparent.png", ["--aspect", "1:1"], 1, "aspect-mismatch"),
            ("missing.png", [], 1, "file-not-found"),
            ("corrupt.png", [], 1, "image-cannot-be-decoded"),
        ]
        for name, options, expected_exit, reason in cases:
            run = subprocess.run([sys.executable, str(checker), str(root / name), *options], capture_output=True, text=True)
            assert run.returncode == expected_exit, (name, run.stderr, run.stdout)
            result = json.loads(run.stdout)
            assert result["ok"] is (expected_exit == 0), result
            if reason:
                assert reason == result.get("error") or reason in result["failures"], result
        for options in [["--aspect", "0:1"], ["--aspect", "nan:1"], ["--min-width", "0"]]:
            run = subprocess.run([sys.executable, str(checker), str(root / "transparent.png"), *options], capture_output=True, text=True)
            assert run.returncode == 2, (options, run.stdout, run.stderr)
        # -S emulates an interpreter without installed Pillow.
        run = subprocess.run([sys.executable, "-S", str(checker), str(root / "transparent.png")], capture_output=True, text=True)
        assert run.returncode == 2 and json.loads(run.stdout)["error"] == "missing-pillow"
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}
        assert after == before, "checker changed input files"
        print("PASS: 12 image cases, 3 invalid arguments, missing dependency, source hashes unchanged")


if __name__ == "__main__":
    main()

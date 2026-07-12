from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "datasets" / "VisDrone"
DST = ROOT / "data" / "datasets" / "VisDrone_merged"
SPLITS = ("train", "val", "test")


def map_class(cls_id: int) -> int:
    if cls_id in (0, 1):
        return 0
    if 2 <= cls_id <= 10:
        return cls_id - 1
    raise ValueError(f"Unexpected class id: {cls_id}")


def link_or_copy_images(src_dir: Path, dst_dir: Path) -> None:
    if dst_dir.exists():
        return
    dst_dir.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(dst_dir), str(src_dir)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"  junction: {dst_dir.name} -> {src_dir}")
            return
        print(f"  junction failed ({result.stderr.strip()}), copying instead...")
    shutil.copytree(src_dir, dst_dir)
    print(f"  copied images: {dst_dir}")


def remap_labels(src_labels: Path, dst_labels: Path) -> tuple[int, int]:
    dst_labels.mkdir(parents=True, exist_ok=True)
    n_files = 0
    n_lines = 0
    for lbl in src_labels.glob("*.txt"):
        out_lines = []
        for line in lbl.read_text(encoding="utf-8").strip().splitlines():
            if not line.strip():
                continue
            parts = line.split()
            cls_id = int(parts[0])
            parts[0] = str(map_class(cls_id))
            out_lines.append(" ".join(parts))
            n_lines += 1
        (dst_labels / lbl.name).write_text("\n".join(out_lines) + ("\n" if out_lines else ""), encoding="utf-8")
        n_files += 1
    return n_files, n_lines


def verify_max_class(labels_dir: Path) -> int:
    max_id = -1
    for lbl in labels_dir.glob("*.txt"):
        for line in lbl.read_text(encoding="utf-8").strip().splitlines():
            if line.strip():
                max_id = max(max_id, int(line.split()[0]))
    return max_id


def main() -> None:
    if not SRC.exists():
        raise FileNotFoundError(f"Source dataset not found: {SRC}")

    print(f"SRC: {SRC}")
    print(f"DST: {DST}")
    DST.mkdir(parents=True, exist_ok=True)

    for split in SPLITS:
        print(f"\n[{split}]")
        src_img = SRC / "images" / split
        dst_img = DST / "images" / split
        src_lbl = SRC / "labels" / split
        dst_lbl = DST / "labels" / split

        if not src_img.exists() or not src_lbl.exists():
            raise FileNotFoundError(f"Missing {split}: {src_img} or {src_lbl}")

        link_or_copy_images(src_img, dst_img)
        n_files, n_lines = remap_labels(src_lbl, dst_lbl)
        max_id = verify_max_class(dst_lbl)
        print(f"  labels: {n_files} files, {n_lines} boxes, max_class_id={max_id}")

    print("\nDone.")

if __name__ == "__main__":
    main()
"""Packs square PNGs into one .ico (PNG-in-ICO, supported by all current browsers).

Usage: python3 make_ico.py out.ico a.png b.png ...
"""
import struct
import sys
from pathlib import Path


def png_size(data: bytes) -> int:
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    width, height = struct.unpack(">II", data[16:24])
    if width != height or width > 256:
        raise ValueError(f"icon must be square and at most 256 px, got {width}x{height}")
    return width


def main(out: str, inputs: list[str]) -> None:
    images = [Path(p).read_bytes() for p in inputs]
    offset = 6 + 16 * len(images)
    entries = b""
    for data in images:
        size = png_size(data) % 256  # 256 is written as 0 in the ICO header
        entries += struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    Path(out).write_bytes(struct.pack("<HHH", 0, 1, len(images)) + entries + b"".join(images))
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])

"""Generate resource-only effect overrides that do not replace SA projectile art.

The player-facing ZIP still contains only resources. The only effect override emitted
here suppresses the shared EntitySlashEffect slash-light visual. Drive/Wave and
Judgement Cut renderer assets are deliberately left to the installed Resharped mod.
"""
from __future__ import annotations

from pathlib import Path
import struct
import zlib

SLASH_OBJ = "assets/slashblade/model/util/slash.obj"
SLASH_PNG = "assets/slashblade/model/util/slash.png"


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (struct.pack(">I", len(payload)) + kind + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))


def rgba_png(width: int, height: int, pixel) -> bytes:
    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            row.extend(pixel(x, y, width, height))
        rows.append(bytes(row))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + _chunk(b"IEND", b""))


def suppressed_slash_png() -> bytes:
    """Fully transparent fallback for Resharped's hard-coded slash texture path."""
    return rgba_png(1, 1, lambda *_: (0, 0, 0, 0))


def suppressed_slash_obj() -> str:
    """Tiny valid base mesh paired with the transparent slash texture."""
    e = 0.000001
    return (
        "# Generated invisible slash-light suppression mesh.\n"
        f"v {-e:.6f} 0.000000 {-e:.6f}\n"
        f"v { e:.6f} 0.000000 {-e:.6f}\n"
        f"v { e:.6f} 0.000000 { e:.6f}\n"
        f"v {-e:.6f} 0.000000 { e:.6f}\n"
        "vt 0.000000 0.000000\n"
        "vt 1.000000 0.000000\n"
        "vt 1.000000 1.000000\n"
        "vt 0.000000 1.000000\n"
        "g base\n"
        "f 1/1 2/2 3/3 4/4\n"
    )


def generate(pack: Path) -> dict[str, bytes]:
    # Do not emit drive.obj/ss.png here. drive_horizontal, drive_vertical and
    # wave_edge all render through EntityDrive/DriveRenderer, so overriding those
    # paths globally changes Slash Art projectile art and third-party users too.
    assets = {
        SLASH_OBJ: suppressed_slash_obj().encode("utf-8"),
        SLASH_PNG: suppressed_slash_png(),
    }
    for rel, payload in assets.items():
        path = pack / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    return assets


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    generated = generate(args.output)
    for name, payload in generated.items():
        print(f"{name}: {len(payload)} bytes")

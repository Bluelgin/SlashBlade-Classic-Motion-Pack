"""Generate resource-only visual adapters for Resharped's fixed render contracts.

The player-facing ZIP still contains only resources. This development-time generator
suppresses the modern slash-light mesh (the classic trail cannot be reproduced
faithfully by a resource pack) while retaining the source-derived r32 Drive geometry.
"""
from __future__ import annotations

from pathlib import Path
import struct
import zlib

SLASH_OBJ = "assets/slashblade/model/util/slash.obj"
SLASH_PNG = "assets/slashblade/model/util/slash.png"
DRIVE_OBJ = "assets/slashblade/model/util/drive.obj"
DRIVE_PNG = "assets/slashblade/model/util/ss.png"


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (struct.pack(">I", len(payload)) + kind + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))


def rgba_png(width: int, height: int, pixel) -> bytes:
    rows = []
    for y in range(height):
        row = bytearray([0])  # PNG filter type 0
        for x in range(width):
            row.extend(pixel(x, y, width, height))
        rows.append(bytes(row))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + _chunk(b"IEND", b""))


def suppressed_slash_png() -> bytes:
    """Fully transparent fallback for the hard-coded slash texture path.

    Omitting slash.png would expose Resharped's modern slash light again. Keeping a
    transparent override makes the visual suppression deterministic while leaving
    EntitySlashEffect gameplay/timing/network behavior untouched.
    """
    return rgba_png(1, 1, lambda *_: (0, 0, 0, 0))


def suppressed_slash_obj() -> str:
    """Tiny valid base mesh used together with the transparent slash texture.

    The quad is intentionally microscopic but non-degenerate, avoiding parser/normal
    edge cases while remaining invisible even if a renderer mishandles alpha.
    """
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


def classic_drive_png() -> bytes:
    """Small neutral luminous mask; DriveRenderer supplies the actual color."""
    def pixel(x: int, y: int, w: int, h: int):
        u = x / (w - 1)
        v = y / (h - 1)
        edge = max(0.0, 1.0 - max(abs(u - 0.5), abs(v - 0.5)) / 0.5)
        alpha = int(255 * min(1.0, 0.45 + 0.75 * edge))
        return 255, 255, 255, alpha

    return rgba_png(16, 16, pixel)


# r32 RenderDrive procedural prism from the pinned Java source. These source
# coordinates are data/geometry expressed in code, not a copied binary model.
_R32_DRIVE = (
    (0, 1, -0.5), (0, 0.75, 0), (0.1, 0.6, -0.15), (0, 0.5, -0.25),
    (-0.1, 0.6, -0.15), (0, 0, 0.25), (0.25, 0, 0), (0, 0, -0.25),
    (-0.25, 0, 0), (0, -0.75, 0), (0.1, -0.6, -0.15), (0, -0.5, -0.25),
    (-0.1, -0.6, -0.15), (0, -1, -0.5),
)
_R32_DRIVE_FACES = (
    (0, 1, 2, 3), (0, 3, 4, 1), (1, 5, 6, 2), (3, 2, 6, 7),
    (3, 7, 8, 4), (1, 4, 8, 5), (6, 5, 9, 10), (6, 10, 11, 7),
    (8, 7, 11, 12), (8, 12, 9, 5), (10, 9, 13, 11), (12, 11, 13, 9),
)


def classic_drive_obj() -> str:
    """Bake r32's procedural Drive prism into Resharped's fixed OBJ contract.

    r32 squeezed local X to 0.25. Resharped uniformly scales the OBJ by 0.015
    and rotates it +90 degrees around Y, so pre-transform the source points to
    preserve the legacy prism silhouette under the modern renderer.
    """
    inv = 1.0 / 0.015
    lines = ["# Generated from the documented r32 procedural Drive prism; adapted to Resharped axes."]
    verts = []
    for x, y, z in _R32_DRIVE:
        px, py, pz = x * 0.25, y, z
        vx, vy, vz = -pz * inv, py * inv, px * inv
        verts.append((vx, vy, vz))
        lines.append(f"v {vx:.6f} {vy:.6f} {vz:.6f}")
    for x, y, z in verts:
        u = max(0.0, min(1.0, 0.5 + z / 12.0))
        v = max(0.0, min(1.0, 0.5 + y / 140.0))
        lines.append(f"vt {u:.6f} {v:.6f}")
    lines.append("g base")
    for face in _R32_DRIVE_FACES:
        ids = [i + 1 for i in face]
        lines.append("f " + " ".join(f"{i}/{i}" for i in ids))
    return "\n".join(lines) + "\n"


def generate(pack: Path) -> dict[str, bytes]:
    assets = {
        SLASH_OBJ: suppressed_slash_obj().encode("utf-8"),
        SLASH_PNG: suppressed_slash_png(),
        DRIVE_OBJ: classic_drive_obj().encode("utf-8"),
        DRIVE_PNG: classic_drive_png(),
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

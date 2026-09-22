"""Generate original classic-style effect assets for Resharped's fixed render contracts.

The player-facing ZIP still contains only resources. This development-time generator
adapts the visual language of the r32 trail/Drive renderers to the resource paths
hard-coded by SlashBlade: Resharped.
"""
from __future__ import annotations

import math
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


def classic_trail_png() -> bytes:
    """Neutral alpha mask for Resharped's color/rank passes.

    U is travel direction and V is ribbon thickness. The thin bright core plus
    quickly fading head/tail reproduces the old afterimage language without
    copying the legacy trail texture.
    """
    def pixel(x: int, y: int, w: int, h: int):
        u = x / (w - 1)
        v = y / (h - 1)
        tail = min(1.0, u / 0.18)
        head = min(1.0, (1.0 - u) / 0.10)
        longitudinal = (tail * head) ** 0.55
        edge = max(0.0, 1.0 - abs(v - 0.5) / 0.5)
        soft = edge ** 0.70
        core = max(0.0, 1.0 - abs(v - 0.52) / 0.16)
        alpha = int(255 * longitudinal * min(1.0, 0.68 * soft + 0.52 * core))
        rgb = int(220 + 35 * core)
        return rgb, rgb, rgb, alpha

    return rgba_png(128, 32, pixel)


def classic_drive_png() -> bytes:
    """Small neutral luminous mask; DriveRenderer supplies the actual color."""
    def pixel(x: int, y: int, w: int, h: int):
        u = x / (w - 1)
        v = y / (h - 1)
        edge = max(0.0, 1.0 - max(abs(u - 0.5), abs(v - 0.5)) / 0.5)
        alpha = int(255 * min(1.0, 0.45 + 0.75 * edge))
        return 255, 255, 255, alpha

    return rgba_png(16, 16, pixel)


def classic_trail_obj(segments: int = 28) -> str:
    """Create a narrow tapered crescent for the global EntitySlashEffect renderer.

    Resharped later flattens Y and scales X/Z to about 3 percent. A much narrower
    swept ribbon than the modern radial disc stays visually attached to the
    classic blade path even though Java still owns effect lifetime/rotation.
    """
    lines = ["# Generated classic trail adapter; no upstream mesh data copied."]
    vertices = []
    uvs = []
    start = math.radians(-72.0)
    sweep = math.radians(116.0)
    for i in range(segments + 1):
        t = i / segments
        angle = start + sweep * t
        envelope = math.sin(math.pi * t) ** 0.58
        bias = 0.88 + 0.12 * t
        half_width = 1.4 + 8.8 * envelope * bias
        center_radius = 66.0 + 5.0 * math.sin(math.pi * t)
        for side in (-1.0, 1.0):
            radius = center_radius + side * half_width
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            y = 0.30 * envelope
            vertices.append((x, y, z))
            uvs.append((t, 0.0 if side < 0 else 1.0))

    for x, y, z in vertices:
        lines.append(f"v {x:.6f} {y:.6f} {z:.6f}")
    for u, v in uvs:
        lines.append(f"vt {u:.6f} {v:.6f}")
    lines.append("g base")
    for i in range(segments):
        a = 2 * i + 1
        b = a + 1
        c = a + 3
        d = a + 2
        lines.append(f"f {a}/{a} {b}/{b} {c}/{c} {d}/{d}")
    return "\n".join(lines) + "\n"


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
        SLASH_OBJ: classic_trail_obj().encode("utf-8"),
        SLASH_PNG: classic_trail_png(),
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

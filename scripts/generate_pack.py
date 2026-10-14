from __future__ import annotations

import io
import json
import os
import random
import uuid
import zipfile
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageColor, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"
PACK_DIR = BUILD_DIR / "BrightFullPack"
OUTPUT_MCPACK = BUILD_DIR / "BrightFullPack.mcpack"

random.seed(42)


def ensure_dirs() -> None:
    PACK_DIR.mkdir(parents=True, exist_ok=True)
    for rel in [
        "textures/blocks",
        "textures/items",
        "textures/ui",
        "textures/colormap",
        "textures/entity",
        "texts",
    ]:
        (PACK_DIR / rel).mkdir(parents=True, exist_ok=True)


def colorize(hex_color: str, brightness: float = 1.0) -> tuple[int, int, int, int]:
    r, g, b = ImageColor.getrgb(hex_color)
    r = max(0, min(255, int(r * brightness)))
    g = max(0, min(255, int(g * brightness)))
    b = max(0, min(255, int(b * brightness)))
    return (r, g, b, 255)


def add_noise(img: Image.Image, amount: int = 18, strength: float = 0.12) -> Image.Image:
    if amount <= 0:
        return img
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            n = random.randint(-amount, amount)
            rr = max(0, min(255, int(r + n * strength)))
            gg = max(0, min(255, int(g + n * strength)))
            bb = max(0, min(255, int(b + n * strength)))
            pixels[x, y] = (rr, gg, bb, a)
    return img


def add_inner_glow(img: Image.Image, glow_color: tuple[int, int, int], opacity: int = 24) -> Image.Image:
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    center = (img.size[0] / 2, img.size[1] / 2)
    max_radius = max(img.size) / 2
    for radius in range(int(max_radius), 0, -1):
        alpha = int(opacity * (radius / max_radius))
        draw.ellipse(
            [center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius],
            outline=(*glow_color, alpha),
            width=2,
        )
    return Image.alpha_composite(img, glow)


def generate_pattern_block(size: int, base: str, highlight: str, shadow: str, noise: int = 20) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, size, size), fill=colorize(base, 1.05))

    for y in range(0, size, 2):
        for x in range(0, size, 2):
            v = (x * 13 + y * 7) % 27
            if v < 11:
                d.rectangle((x, y, x + 2, y + 2), fill=colorize(highlight, 1.10))
            elif v > 18:
                d.rectangle((x, y, x + 2, y + 2), fill=colorize(shadow, 0.92))

    img = add_noise(img, amount=noise, strength=0.18)
    return img


def generate_grass_top() -> Image.Image:
    img = generate_pattern_block(16, "#69d35d", "#9cf686", "#4daa3d", noise=16)
    d = ImageDraw.Draw(img)
    for y in range(0, 16, 4):
        for x in range(0, 16, 4):
            if (x + y) % 8 == 0:
                d.rectangle((x, y, x + 3, y + 3), fill=(255, 255, 255, 40))
    return img


def generate_dirt() -> Image.Image:
    img = generate_pattern_block(16, "#8f5e32", "#b9844a", "#6f4928", noise=20)
    return img


def generate_stone() -> Image.Image:
    img = generate_pattern_block(16, "#7d7d88", "#a3a3b2", "#5f5f6d", noise=18)
    return img


def generate_sand() -> Image.Image:
    img = generate_pattern_block(16, "#e7d694", "#f4e6a9", "#c7b56f", noise=18)
    return img


def generate_planks() -> Image.Image:
    img = Image.new("RGBA", (16, 16), colorize("#e2b574", 1.2))
    d = ImageDraw.Draw(img)
    for x in range(0, 16, 4):
        d.line((x, 0, x, 15), fill=(120, 90, 55, 90), width=1)
    for y in range(0, 16, 4):
        d.line((0, y, 15, y), fill=(160, 130, 90, 80), width=1)
    img = add_noise(img, amount=12, strength=0.15)
    return img


def generate_log() -> Image.Image:
    img = Image.new("RGBA", (16, 16), colorize("#b47a3a", 1.1))
    d = ImageDraw.Draw(img)
    for x in range(0, 16, 4):
        d.rectangle((x, 0, x + 2, 15), fill=(80, 55, 30, 120))
    for y in range(0, 16, 4):
        d.rectangle((0, y, 15, y + 2), fill=(120, 85, 42, 120))
    img = add_noise(img, amount=12, strength=0.12)
    return img


def generate_leaves() -> Image.Image:
    img = Image.new("RGBA", (16, 16), colorize("#56d76b", 1.1))
    d = ImageDraw.Draw(img)
    for i in range(0, 15, 3):
        d.ellipse((i, i // 2, i + 7, i + 7), fill=(255, 255, 255, 42))
    img = add_noise(img, amount=16, strength=0.16)
    return img


def generate_glass() -> Image.Image:
    base = Image.new("RGBA", (16, 16), (160, 220, 255, 120))
    d = ImageDraw.Draw(base)
    for x in range(0, 16, 4):
        d.line((x, 0, x, 15), fill=(255, 255, 255, 55), width=1)
    for y in range(0, 16, 4):
        d.line((0, y, 15, y), fill=(255, 255, 255, 55), width=1)
    return base


def generate_water() -> Image.Image:
    img = Image.new("RGBA", (16, 16), (42, 112, 255, 180))
    d = ImageDraw.Draw(img)
    for i in range(0, 17, 4):
        d.line((i, 0, i + 2, 15), fill=(150, 220, 255, 110), width=1)
    return img


def generate_torch() -> Image.Image:
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((6, 2, 9, 15), radius=2, fill=(184, 130, 78, 220))
    d.ellipse((3, 0, 12, 12), fill=(255, 214, 110, 220))
    d.ellipse((4, 1, 11, 10), fill=(255, 247, 170, 200))
    return img


def generate_ore(base: str, sparkle: str) -> Image.Image:
    img = generate_pattern_block(16, base, sparkle, "#444444", noise=12)
    glow = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    for i in range(4):
        x = 2 + i * 4
        y = 1 + (i % 2) * 5
        d.ellipse((x, y, x + 3, y + 3), fill=(255, 255, 255, 50))
    img = Image.alpha_composite(img, glow)
    return img


def generate_item_texture(name: str, base: str, accent: str, shape: str = "square") -> Image.Image:
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if shape == "square":
        d.rounded_rectangle((3, 3, 12, 12), radius=2, fill=colorize(base, 1.1))
        d.rounded_rectangle((5, 5, 10, 10), radius=2, fill=colorize(accent, 1.25))
    elif shape == "diamond":
        points = [(8, 1), (15, 8), (8, 15), (1, 8)]
        d.polygon(points, fill=colorize(base, 1.1))
        d.polygon([(8, 4), (12, 8), (8, 12), (4, 8)], fill=colorize(accent, 1.25))
    elif shape == "stick":
        d.rounded_rectangle((7, 1, 9, 15), radius=1, fill=colorize(base, 1.15))
        d.rounded_rectangle((6, 3, 10, 13), radius=1, fill=colorize(accent, 1.25))
    else:
        d.ellipse((2, 2, 14, 14), fill=colorize(base, 1.1))
        d.ellipse((5, 5, 11, 11), fill=colorize(accent, 1.25))
    return img


def write_image(path: Path, img: Image.Image) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def write_manifest() -> None:
    package_uuid = str(uuid.uuid4())
    module_uuid = str(uuid.uuid4())
    manifest = {
        "format_version": 2,
        "header": {
            "name": "BrightFull Pack",
            "description": "Fullbright-ish bright resource pack for Bedrock MCPE/BE.",
            "uuid": package_uuid,
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0],
        },
        "modules": [
            {
                "type": "resources",
                "uuid": module_uuid,
                "description": "Bright textures and UI assets",
                "version": [1, 0, 0],
            }
        ],
    }
    (PACK_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def write_lang_file() -> None:
    lines = [
        "item.heart=Heart",
        "item.stick=Stick",
        "item.diamond=Diamond",
        "tile.grass.name=Bright Grass",
        "tile.dirt.name=Bright Dirt",
        "tile.stone.name=Bright Stone",
        "tile.sand.name=Bright Sand",
        "tile.torch.name=Torch",
        "tile.glass.name=Glass",
        "tile.log.name=Bright Log",
        "tile.leaves.name=Bright Leaves",
    ]
    (PACK_DIR / "texts" / "en_US.lang").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_pack_icon() -> None:
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((8, 8, 56, 56), radius=10, fill=(255, 203, 69, 255))
    d.ellipse((18, 18, 46, 46), fill=(255, 245, 184, 255))
    d.line((32, 18, 32, 46), fill=(64, 94, 255, 255), width=4)
    d.line((18, 32, 46, 32), fill=(64, 94, 255, 255), width=4)
    img.save(PACK_DIR / "pack_icon.png")


def generate_textures() -> None:
    write_image(PACK_DIR / "textures/blocks/grass_block_top.png", generate_grass_top())
    write_image(PACK_DIR / "textures/blocks/dirt.png", generate_dirt())
    write_image(PACK_DIR / "textures/blocks/stone.png", generate_stone())
    write_image(PACK_DIR / "textures/blocks/sand.png", generate_sand())
    write_image(PACK_DIR / "textures/blocks/planks_oak.png", generate_planks())
    write_image(PACK_DIR / "textures/blocks/log_oak.png", generate_log())
    write_image(PACK_DIR / "textures/blocks/leaves_oak.png", generate_leaves())
    write_image(PACK_DIR / "textures/blocks/glass.png", generate_glass())
    write_image(PACK_DIR / "textures/blocks/water_still.png", generate_water())
    write_image(PACK_DIR / "textures/blocks/torch_on.png", generate_torch())
    write_image(PACK_DIR / "textures/blocks/iron_ore.png", generate_ore("#8b97a7", "#d5e1f4"))
    write_image(PACK_DIR / "textures/blocks/gold_ore.png", generate_ore("#c9a84b", "#ffe6a2"))
    write_image(PACK_DIR / "textures/blocks/diamond_ore.png", generate_ore("#6ad7ff", "#c6f5ff"))

    write_image(PACK_DIR / "textures/items/stick.png", generate_item_texture("stick", "#d6b77d", "#f2dfaf", "stick"))
    write_image(PACK_DIR / "textures/items/diamond.png", generate_item_texture("diamond", "#7ee8ff", "#d9faff", "diamond"))
    write_image(PACK_DIR / "textures/items/heart.png", generate_item_texture("heart", "#ff5b78", "#ffc2c8", "circle"))

    # UI placeholders for a bright, readable presentation
    ui = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(ui)
    d.rectangle((1, 1, 15, 15), fill=(255, 220, 94, 220))
    write_image(PACK_DIR / "textures/ui/heart.png", ui)


def create_zip() -> None:
    with zipfile.ZipFile(OUTPUT_MCPACK, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(PACK_DIR):
            for filename in files:
                path = Path(root) / filename
                rel = path.relative_to(BUILD_DIR)
                zf.write(path, arcname=str(rel))


def main() -> None:
    ensure_dirs()
    write_manifest()
    write_pack_icon()
    write_lang_file()
    generate_textures()
    create_zip()
    print(f"Created package at: {OUTPUT_MCPACK}")
    print(f"Generated resource folder at: {PACK_DIR}")


if __name__ == "__main__":
    main()

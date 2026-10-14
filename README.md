# BrightFull Pack

A public Bedrock resource pack generator for a cheerful, permanently bright, not-too-serious fullbright look. This repo contains a generator script that creates a Bedrock-compatible `mcpack` resource pack using 16×/32×/64× textures, plus a brightened UI and terrain set.

## What this is

This is a texture-only fullbright approach for Minecraft Bedrock/MCPE:
- brighter terrain textures
- subtle emissive highlights
- cleaner readability in caves, caves, and nighttime scenes
- a colorful, light-hearted visual feel that is not overly realistic

It does not change the game's actual lighting engine. For real engine-level fullbright, a behavior pack or client mod would be required.

## Repo structure

- `scripts/generate_pack.py` — builds the resource pack.
- `build/` — output folder for generated files.

## Requirements

- Python 3.10+
- Pillow (`pip install pillow`)

## Build the pack

```bash
python -m pip install pillow
python scripts/generate_pack.py
```

This script creates:
- `build/BrightFullPack.mcpack`
- `build/BrightFullPack/manifest.json`
- generated textures in `build/BrightFullPack/textures/...`
- `build/BrightFullPack/texts/en_US.lang`
- `build/BrightFullPack/pack_icon.png`

## Install

1. Open the generated `.mcpack` file with Minecraft Bedrock/MCPE.
2. Or unzip the generated folder into your resource pack folder.
3. Enable the pack in Settings → Global Resources.

## Notes

This is intentionally bright and easy to read, with a playful visual style. If you want the next iteration, I can push a darker realistic pass, a more crisp 64× version, or add a stronger glow treatment for blocks like stone, ores, and torches.

## License

CC0. You can use, remix, and redistribute this pack freely.

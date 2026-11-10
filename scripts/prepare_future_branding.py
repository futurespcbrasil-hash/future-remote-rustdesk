#!/usr/bin/env python3
"""Prepare the official Future Soluções logo for the light and dark app themes."""
from pathlib import Path
import sys

from PIL import Image, ImageOps

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: prepare_future_branding.py <official-logo.png>", file=sys.stderr)
        return 2

    source_path = Path(sys.argv[1])
    if not source_path.is_file():
        print(f"Official Future logo not found: {source_path}", file=sys.stderr)
        return 2

    with Image.open(source_path) as opened:
        source = opened.convert("RGBA")

    if source.width < 150 or source.height < 40:
        print(f"Official Future logo has unexpected dimensions: {source.size}", file=sys.stderr)
        return 3

    assets = Path("flutter/assets")
    assets.mkdir(parents=True, exist_ok=True)

    # The light variant is the exact official PNG supplied by Future Soluções.
    light_path = assets / "future-logo-light.png"
    source.save(light_path, format="PNG", optimize=True)

    # The app's compact icon uses the official shield mark from the left of the logo.
    side = min(source.width, source.height)
    mark = source.crop((0, 0, side, side))
    icon_canvas = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
    mark = ImageOps.contain(mark, (440, 440), method=Image.Resampling.LANCZOS)
    icon_canvas.alpha_composite(mark, ((512 - mark.width) // 2, (512 - mark.height) // 2))
    icon_path = assets / "icon.png"
    icon_canvas.save(icon_path, format="PNG", optimize=True)

    # Keep the original shield and yellow accent intact. Only recolor the dark
    # wordmark on the right so the official logo remains readable in dark mode.
    dark = source.copy()
    pixels = dark.load()
    wordmark_start = int(source.width * 0.34)
    for y in range(source.height):
        for x in range(wordmark_start, source.width):
            red, green, blue, alpha = pixels[x, y]
            if alpha == 0:
                continue
            luminance = (red * 299 + green * 587 + blue * 114) // 1000
            if luminance < 175:
                pixels[x, y] = (255, 255, 255, alpha)

    dark_path = assets / "future-logo-dark.png"
    dark.save(dark_path, format="PNG", optimize=True)

    for path in (light_path, dark_path, icon_path):
        if not path.is_file() or path.stat().st_size < 1000:
            print(f"Future logo asset validation failed: {path}", file=sys.stderr)
            return 4

    print(f"Prepared official Future Soluções theme logos: {light_path}, {dark_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

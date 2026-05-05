"""
Extract a dominant-color palette from a logo image.

Usage: python3 extract_palette.py <image_path>
Outputs: 5 hex codes, one per line, sorted by visual prominence.

Handles PNG/JPG via Pillow; handles SVG by:
  1. Parsing fill colors directly from the XML (works for most clean logos), OR
  2. Rasterizing via cairosvg if installed and falling back to PIL quantization.
"""
import sys
import re
from pathlib import Path
from PIL import Image
import io


def parse_svg_fills(svg_text):
    """Extract fill colors from an SVG via regex on fill="..." and fill: ... ."""
    colors = []
    seen = set()

    # Match fill="#RRGGBB" or fill='#RRGGBB' (also #RGB short form)
    for m in re.finditer(r'fill\s*[=:]\s*["\']?(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})', svg_text):
        c = m.group(1).upper()
        # Expand 3-digit hex to 6-digit
        if len(c) == 4:
            c = "#" + "".join(ch * 2 for ch in c[1:])
        if c not in seen:
            seen.add(c)
            colors.append(c)

    # Also match rgb(r,g,b) fills
    for m in re.finditer(r'fill\s*[=:]\s*["\']?rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', svg_text):
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        c = f"#{r:02X}{g:02X}{b:02X}"
        if c not in seen:
            seen.add(c)
            colors.append(c)

    return colors


def filter_palette(colors):
    """Drop pure white/black/grey, keep distinct branded colors."""
    out = []
    for c in colors:
        r = int(c[1:3], 16)
        g = int(c[3:5], 16)
        b = int(c[5:7], 16)
        if r > 240 and g > 240 and b > 240:  # near-white
            continue
        if r < 12 and g < 12 and b < 12:  # near-black
            continue
        mx, mn = max(r, g, b), min(r, g, b)
        sat = (mx - mn) / max(mx, 1)
        bri = (r + g + b) / 3
        # Skip pure greys (low saturation mid-brightness)
        if sat < 0.05 and 80 < bri < 200:
            continue
        out.append(c)
    return out


def extract_from_raster(image_path, n_colors=5, n_pool=24):
    """Use median-cut quantization on a raster image."""
    img = Image.open(image_path)
    if img.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", img.size, (220, 220, 220))
        alpha = img.split()[-1]
        rgb = img.convert("RGB")
        bg.paste(rgb, mask=alpha)
        img = bg
    else:
        img = img.convert("RGB")

    quantized = img.quantize(colors=n_pool, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()
    color_counts = sorted(quantized.getcolors(), reverse=True)

    selected = []
    seen = set()
    for count, idx in color_counts:
        r = palette[idx * 3]
        g = palette[idx * 3 + 1]
        b = palette[idx * 3 + 2]
        if r > 240 and g > 240 and b > 240: continue
        if r < 12 and g < 12 and b < 12: continue
        mx, mn = max(r, g, b), min(r, g, b)
        sat = (mx - mn) / max(mx, 1)
        bri = (r + g + b) / 3
        if sat < 0.05 and 80 < bri < 200: continue

        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        if hex_color in seen: continue
        seen.add(hex_color)
        selected.append((hex_color, count, sat, bri))

    def rank(item):
        hx, count, sat, bri = item
        return (0 if sat > 0.25 else 1, -count)

    selected.sort(key=rank)
    return [hx for hx, *_ in selected[:n_colors]]


def extract_from_svg(svg_path, n_colors=5):
    """Parse SVG XML for fill colors. Falls back to cairosvg rasterization if needed."""
    text = Path(svg_path).read_text(errors="ignore")

    # Direct parse from fill attributes
    colors = parse_svg_fills(text)
    colors = filter_palette(colors)
    if len(colors) >= 3:
        return colors[:n_colors]

    # Fallback: rasterize with cairosvg if available
    try:
        import cairosvg
        png_bytes = cairosvg.svg2png(url=str(svg_path), output_width=512)
        img = Image.open(io.BytesIO(png_bytes))
        # Save tmp for the raster path
        tmp = Path("/tmp/_palette_tmp.png")
        img.save(tmp)
        return extract_from_raster(tmp, n_colors=n_colors)
    except ImportError:
        # Last resort: return whatever fills we got, even if few
        return colors[:n_colors] if colors else []


def extract_palette(image_path, n_colors=5):
    p = Path(image_path)
    if p.suffix.lower() == ".svg":
        return extract_from_svg(p, n_colors)
    return extract_from_raster(p, n_colors)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_palette.py <image_path>", file=sys.stderr)
        sys.exit(1)
    image_path = Path(sys.argv[1])
    if not image_path.exists():
        print(f"File not found: {image_path}", file=sys.stderr)
        sys.exit(1)
    palette = extract_palette(image_path)
    if not palette:
        print("No palette could be extracted (logo may be all-white or unreadable)", file=sys.stderr)
        sys.exit(2)
    for c in palette:
        print(c)

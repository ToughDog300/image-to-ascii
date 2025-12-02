#!/usr/bin/env python3
from PIL import Image, ImageFilter
import os, sys, html

# palette
CHARS = (
    "@$#B8&WM#*oahkbdpqwmZ0QLCJUYX"
    "zcvunxrjft/\\|()1{}[]?-_+~<>i!"
    "lI;:,\"^`'. "
)

# parameters
TARGET_WIDTH = 120      # wide
GAUSSIAN_BLUR = 0.8     # blur
GAMMA = 1.08            # tone smoothness
LINE_HEIGHT = 0.95      # heigth

def luminance(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b

def map_char_from_lum(lum):
    v = (lum / 255.0) ** (1.0 / GAMMA)
    idx = int(v * (len(CHARS) - 1))
    return CHARS[idx]

def make_html_name(inp_path):
    dirn, fname = os.path.split(inp_path)
    base, _ = os.path.splitext(fname)
    return os.path.join(dirn, f"{base}ASCII.html")

def prepare_image(img, target_width):
    img = img.convert("RGB")
    w, h = img.size
    target_width = min(target_width, max(20, w))
    aspect = h / w
    target_height = max(1, int(aspect * target_width * 0.43))
    if GAUSSIAN_BLUR > 0:
        img = img.filter(ImageFilter.GaussianBlur(radius=GAUSSIAN_BLUR))
    img_small = img.resize((target_width, target_height), resample=Image.LANCZOS)
    return img_small

def build_rows(img_small):
    w, h = img_small.size
    pixels = list(img_small.getdata())
    rows = []
    for y in range(h):
        row = []
        for x in range(w):
            r, g, b = pixels[y * w + x]
            lum = luminance(r, g, b)
            ch = map_char_from_lum(lum)
            row.append((ch, (r, g, b)))
        rows.append(row)
    return rows

def write_html(html_path, rows, title):
    lines = []
    for row in rows:
        parts = []
        for ch, (r, g, b) in row:
            esc = html.escape(ch)
            parts.append(f'<span style="color: rgb({r},{g},{b});">{esc}</span>')
        lines.append("".join(parts))

    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)} — ASCII</title>
<style>
  body {{ background: black; margin: 0; padding: 1rem; }}
  pre {{ font-family: monospace; font-size: 12px; line-height: {LINE_HEIGHT}; white-space: pre; }}
  span {{ font-family: monospace; }}
</style>
</head>
<body>
<pre>
{'\n'.join(lines)}
</pre>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(doc)

def main():
    if len(sys.argv) < 2:
        print("Usage: python image_to_ascii.py <image>")
        sys.exit(1)

    inp = sys.argv[1]
    if not os.path.isfile(inp):
        print("File not found:", inp)
        sys.exit(2)

    try:
        img = Image.open(inp)
    except Exception as e:
        print("Cannot open image:", e)
        sys.exit(3)

    target_w = TARGET_WIDTH if img.width >= TARGET_WIDTH else img.width
    img_small = prepare_image(img, target_w)
    rows = build_rows(img_small)

    html_path = make_html_name(inp)
    try:
        write_html(html_path, rows, os.path.basename(inp))
    except Exception as e:
        print("Error writing HTML:", e)
        sys.exit(4)

    print("Done. HTML saved to:", html_path)
    print("Open it in browser  and embrace the magic!")

if __name__ == "__main__":
    main()

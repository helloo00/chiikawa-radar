#!/usr/bin/env python3
"""Generate the ChiikawaRadar app icon: a rounded 「ち」 over a faint radar."""
import pathlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = pathlib.Path(__file__).parent
OUT_DIR = ROOT / "Assets.xcassets" / "AppIcon.appiconset"
OUT_DIR.mkdir(parents=True, exist_ok=True)
S = 1024

FONT_CANDIDATES = [
    "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/a9507b2dd1e57ecf7dc3a2fe25e8abfef12973ad.asset/AssetData/TsukushiAMaruGothic.ttc",
    "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/60484a5d6f3fa8d51dcbeff43b7e70c9d42bcd2f.asset/AssetData/TsukushiBMaruGothic.ttc",
    "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/b7a6a6575a699e801915b73b9e1e75c74a3404ce.asset/AssetData/YuGothic-Bold.otf",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]


def load_font(size):
    for path in FONT_CANDIDATES:
        if pathlib.Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    raise SystemExit("no usable Japanese font found")


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


# --- background: diagonal rose gradient ---
top_left = (0xD6, 0x66, 0x83)
bot_right = (0xB4, 0x44, 0x63)
bg = Image.new("RGB", (S, S))
px = bg.load()
for y in range(S):
    for x in range(S):
        t = (x + y) / (2 * S)
        px[x, y] = lerp(top_left, bot_right, t)

img = bg.convert("RGBA")
overlay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)

cx = cy = S / 2

# --- faint radar rings ---
for r in (250, 372, 486):
    od.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, 34), width=6)
od.line([cx - 486, cy, cx + 486, cy], fill=(255, 255, 255, 22), width=5)
od.line([cx, cy - 486, cx, cy + 486], fill=(255, 255, 255, 22), width=5)

# --- blip with glow (lower left, clear of the character) ---
bx, by, br = 292, 742, 38
glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([bx - br * 2.4, by - br * 2.4, bx + br * 2.4, by + br * 2.4], fill=(246, 208, 107, 150))
glow = glow.filter(ImageFilter.GaussianBlur(34))
overlay = Image.alpha_composite(overlay, glow)
od = ImageDraw.Draw(overlay)
od.ellipse([bx - br, by - br, bx + br, by + br], fill=(246, 208, 107, 255))
od.ellipse([bx - br, by - br, bx + br, by + br], outline=(255, 255, 255, 235), width=8)

img = Image.alpha_composite(img, overlay)

# --- the 「ち」 ---
draw = ImageDraw.Draw(img)
font = load_font(660)
stroke = 26
text = "ち"
bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx = cx - tw / 2 - bbox[0]
ty = cy - th / 2 - bbox[1] + 8

# soft shadow
shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.text((tx, ty + 20), text, font=font, fill=(120, 30, 50, 150), stroke_width=stroke,
        stroke_fill=(120, 30, 50, 150))
shadow = shadow.filter(ImageFilter.GaussianBlur(18))
img = Image.alpha_composite(img, shadow)

draw = ImageDraw.Draw(img)
draw.text((tx, ty), text, font=font, fill=(255, 255, 255, 255), stroke_width=stroke,
          stroke_fill=(255, 255, 255, 255))

img.convert("RGB").save(OUT_DIR / "icon-1024.png")

(OUT_DIR / "Contents.json").write_text(
    '{\n'
    '  "images" : [\n'
    '    {\n'
    '      "filename" : "icon-1024.png",\n'
    '      "idiom" : "universal",\n'
    '      "platform" : "ios",\n'
    '      "size" : "1024x1024"\n'
    '    }\n'
    '  ],\n'
    '  "info" : { "author" : "xcode", "version" : 1 }\n'
    '}\n'
)
(ROOT / "Assets.xcassets" / "Contents.json").write_text(
    '{\n  "info" : { "author" : "xcode", "version" : 1 }\n}\n'
)
print("wrote", OUT_DIR / "icon-1024.png")

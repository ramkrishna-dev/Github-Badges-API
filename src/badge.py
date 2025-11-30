from typing import Optional
import re
from .utils import sanitize_string

THEMES = {
    "flat": {
        "rect": '<rect width="100%" height="100%" fill="{bg_color}"/>',
        "text": '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{text_color}" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="{font_size}">{text}</text>',
        "bg_color": "#555",
        "text_color": "#fff",
        "height": 20,
    },
    "flat-square": {
        "rect": '<rect width="100%" height="100%" rx="3" fill="{bg_color}"/>',
        "text": '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{text_color}" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="{font_size}">{text}</text>',
        "bg_color": "#555",
        "text_color": "#fff",
        "height": 20,
    },
    "plastic": {
        "rect": '<rect width="100%" height="100%" rx="4" ry="4" fill="url(#a)"/> <defs><linearGradient id="a" x2="0" y2="100%"><stop offset="0" stop-color="#fff" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient></defs>',
        "text": '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{text_color}" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="{font_size}" font-weight="bold">{text}</text>',
        "bg_color": "#555",
        "text_color": "#fff",
        "height": 18,
    },
    "minimal": {
        "rect": '<rect width="100%" height="100%" fill="{bg_color}"/>',
        "text": '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{text_color}" font-family="Arial, sans-serif" font-size="{font_size}">{text}</text>',
        "bg_color": "#4c1",
        "text_color": "#fff",
        "height": 20,
    },
}

COLOR_MAP = {
    "green": "#4c1",
    "yellow": "#dfb317",
    "orange": "#fe7d37",
    "red": "#e05d44",
    "blue": "#007ec6",
    "grey": "#555",
    "lightgrey": "#9f9f9f",
}

def get_color(value: str) -> str:
    if value.isdigit():
        num = int(value)
        if num > 100:
            return "red"
        elif num > 50:
            return "orange"
        else:
            return "green"
    return "blue"

def calculate_width(label: str, value: str, font_size: int) -> int:
    # Rough estimation: 8px per character
    return max(80, len(label) * 8 + len(value) * 8 + 20)

def generate_badge(label: str, value: str, style: str = "flat", color: Optional[str] = None) -> str:
    theme = THEMES.get(style, THEMES["flat"])
    bg_color = COLOR_MAP.get(color, get_color(value)) if color else get_color(value)
    text_color = theme["text_color"]
    height = theme["height"]
    font_size = 11
    width = calculate_width(label, value, font_size)

    rect_svg = theme["rect"].format(bg_color=bg_color)
    text_svg = theme["text"].format(text_color=text_color, font_size=font_size, text=f"{sanitize_string(label)}: {sanitize_string(value)}")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
{rect_svg}
{text_svg}
</svg>'''
    return svg
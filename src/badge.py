from typing import Optional, Dict, Any
import re
from .utils import sanitize_string

# Icon SVGs (inline)
ICONS = {
    "github": '<path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>',
    "star": '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>',
    "flame": '<path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm4.5 9.5c0 1.5-1.5 3-3 3s-3-1.5-3-3c0-1.5 1.5-3 3-3s3 1.5 3 3z"/>',
    "bolt": '<path d="M12 2l-1.5 4.5h-4.5l3.5 2.5-1.5 4.5 3.5-2.5 3.5 2.5-1.5-4.5 3.5-2.5h-4.5z"/>',
}

THEMES = {
    "flat": {
        "template": '''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<rect width="100%" height="100%" fill="{bg_color}"/>
{text}
</svg>''',
        "text_template": '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{text_color}" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="{font_size}">{icon}{label}: {value}</text>',
        "bg_color": "#555",
        "text_color": "#fff",
        "height": 20,
    },
    "flat-square": {
        "template": '''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<rect width="100%" height="100%" rx="3" fill="{bg_color}"/>
{text}
</svg>''',
        "text_template": '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{text_color}" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="{font_size}">{icon}{label}: {value}</text>',
        "bg_color": "#555",
        "text_color": "#fff",
        "height": 20,
    },
    "plastic": {
        "template": '''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<rect width="100%" height="100%" rx="4" ry="4" fill="url(#a)"/>
<defs><linearGradient id="a" x2="0" y2="100%"><stop offset="0" stop-color="#fff" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient></defs>
{text}
</svg>''',
        "text_template": '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{text_color}" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="{font_size}" font-weight="bold">{icon}{label}: {value}</text>',
        "bg_color": "#555",
        "text_color": "#fff",
        "height": 18,
    },
    "minimal": {
        "template": '''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<rect width="100%" height="100%" fill="{bg_color}"/>
{text}
</svg>''',
        "text_template": '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{text_color}" font-family="Arial, sans-serif" font-size="{font_size}">{icon}{label}: {value}</text>',
        "bg_color": "#4c1",
        "text_color": "#fff",
        "height": 20,
    },
    "neon": {
        "template": '''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<defs><linearGradient id="neon" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" style="stop-color:#00ff00"/><stop offset="100%" style="stop-color:#00ffff"/></linearGradient></defs>
<rect width="100%" height="100%" fill="url(#neon)" stroke="#00ff00" stroke-width="2"/>
{text}
</svg>''',
        "text_template": '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#000" font-family="Courier New, monospace" font-size="{font_size}" font-weight="bold">{icon}{label}: {value}</text>',
        "bg_color": "#00ff00",
        "text_color": "#000",
        "height": 20,
    },
    "cyberpunk": {
        "template": '''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<defs><linearGradient id="cyber" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" style="stop-color:#ff0080"/><stop offset="50%" style="stop-color:#8000ff"/><stop offset="100%" style="stop-color:#0080ff"/></linearGradient></defs>
<rect width="100%" height="100%" fill="url(#cyber)"/>
{text}
</svg>''',
        "text_template": '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#fff" font-family="Impact, sans-serif" font-size="{font_size}" text-shadow="1px 1px 2px #000">{icon}{label}: {value}</text>',
        "bg_color": "#ff0080",
        "text_color": "#fff",
        "height": 20,
    },
    "transparent": {
        "template": '''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{text_color}" font-family="Arial, sans-serif" font-size="{font_size}">{icon}{label}: {value}</text>
</svg>''',
        "text_template": '',
        "bg_color": "transparent",
        "text_color": "#000",
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

def calculate_width(label: str, value: str, icon: str = "", font_size: int = 11) -> int:
    icon_width = 16 if icon else 0
    return max(80, len(label) * 8 + len(value) * 8 + icon_width + 20)

def get_icon_svg(icon_name: str) -> str:
    if icon_name in ICONS:
        return f'<g transform="translate(5,2) scale(0.8)">{ICONS[icon_name]}</g> '
    return ""

def generate_badge(label: str, value: str, style: str = "flat", color: Optional[str] = None, icon: str = "", gradient: Optional[str] = None) -> str:
    theme = THEMES.get(style, THEMES["flat"])
    bg_color = COLOR_MAP.get(color, get_color(value)) if color else get_color(value)
    if gradient:
        # Simple gradient support
        bg_color = f"url(#{gradient})"
    text_color = theme["text_color"]
    height = theme["height"]
    font_size = 11
    icon_svg = get_icon_svg(icon)
    width = calculate_width(label, value, icon, font_size)

    if theme["text_template"]:
        text = theme["text_template"].format(
            text_color=text_color, font_size=font_size, icon=icon_svg, label=sanitize_string(label), value=sanitize_string(value)
        )
    else:
        text = f'<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{text_color}" font-family="Arial, sans-serif" font-size="{font_size}">{icon_svg}{sanitize_string(label)}: {sanitize_string(value)}</text>'

    svg = theme["template"].format(width=width, height=height, bg_color=bg_color, text=text)
    return svg
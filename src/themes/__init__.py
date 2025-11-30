from typing import Dict, Any

THEMES: Dict[str, Dict[str, Any]] = {
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
    "glass": {
        "template": '''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<defs><filter id="blur"><feGaussianBlur stdDeviation="2"/></filter></defs>
<rect width="100%" height="100%" fill="{bg_color}" opacity="0.8" filter="url(#blur)"/>
<rect width="100%" height="100%" fill="none" stroke="{bg_color}" stroke-width="1"/>
{text}
</svg>''',
        "text_template": '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{text_color}" font-family="Arial, sans-serif" font-size="{font_size}">{icon}{label}: {value}</text>',
        "bg_color": "#ffffff",
        "text_color": "#000",
        "height": 20,
    },
    "pixel": {
        "template": '''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" style="image-rendering: pixelated;">
<rect width="100%" height="100%" fill="{bg_color}"/>
{text}
</svg>''',
        "text_template": '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{text_color}" font-family="monospace" font-size="10" style="font-weight: bold;">{icon}{label}: {value}</text>',
        "bg_color": "#000",
        "text_color": "#0f0",
        "height": 20,
    },
}

def get_theme(theme_name: str) -> Dict[str, Any]:
    return THEMES.get(theme_name, THEMES["flat"])

def install_theme(url: str) -> bool:
    # Placeholder for theme installation
    # Would download and install theme from URL
    return False
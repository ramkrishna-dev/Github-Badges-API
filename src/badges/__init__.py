from typing import Optional, Dict, Any, List
import re
from ..utils import sanitize_string
from ..themes import get_theme

def calculate_width(label: str, value: str, icon: str = "", font_size: int = 11) -> int:
    icon_width = 16 if icon else 0
    return max(80, len(label) * 8 + len(value) * 8 + icon_width + 20)

def get_icon_svg(icon_name: str) -> str:
    icons = {
        "github": '<path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>',
        "star": '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>',
        "flame": '<path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm4.5 9.5c0 1.5-1.5 3-3 3s-3-1.5-3-3c0-1.5 1.5-3 3-3s3 1.5 3 3z"/>',
        "bolt": '<path d="M12 2l-1.5 4.5h-4.5l3.5 2.5-1.5 4.5 3.5-2.5 3.5 2.5-1.5-4.5 3.5-2.5h-4.5z"/>',
    }
    if icon_name in icons:
        return f'<g transform="translate(5,2) scale(0.8)">{icons[icon_name]}</g> '
    return ""

def generate_badge(label: str, value: str, style: str = "flat", color: Optional[str] = None, icon: str = "", animated: bool = False) -> str:
    theme = get_theme(style)
    bg_color = color or theme.get("bg_color", "#555")
    text_color = theme.get("text_color", "#fff")
    height = theme.get("height", 20)
    font_size = 11
    icon_svg = get_icon_svg(icon)
    width = calculate_width(label, value, icon, font_size)

    # Animation support
    animation = ""
    if animated:
        animation = '''
        <style>
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        rect { animation: pulse 2s infinite; }
        </style>
        '''

    template = theme.get("template", '''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<rect width="100%" height="100%" fill="{bg_color}"/>
{text}
</svg>''')

    text = theme.get("text_template", '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{text_color}" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="{font_size}">{icon}{label}: {value}</text>')
    text = text.format(
        text_color=text_color, font_size=font_size, icon=icon_svg,
        label=sanitize_string(label), value=sanitize_string(value)
    )

    svg = template.format(width=width, height=height, bg_color=bg_color, text=text, animation=animation)
    return svg

def compose_badges(badges: List[Dict[str, Any]], layout: str = "horizontal") -> str:
    """Compose multiple badges into one SVG"""
    if layout == "horizontal":
        total_width = sum(b["width"] for b in badges)
        height = max(b["height"] for b in badges)
        composed = f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{height}">'
        x_offset = 0
        for badge in badges:
            composed += f'<g transform="translate({x_offset}, 0)">{badge["svg"]}</g>'
            x_offset += badge["width"]
        composed += '</svg>'
        return composed
    # Add vertical and matrix layouts as needed
    return ""
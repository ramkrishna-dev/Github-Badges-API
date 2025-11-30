from typing import List, Dict, Any
from .badges import generate_badge

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
    elif layout == "vertical":
        width = max(b["width"] for b in badges)
        total_height = sum(b["height"] for b in badges)
        composed = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_height}">'
        y_offset = 0
        for badge in badges:
            composed += f'<g transform="translate(0, {y_offset})">{badge["svg"]}</g>'
            y_offset += badge["height"]
        composed += '</svg>'
        return composed
    return ""
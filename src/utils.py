# Utility functions

def sanitize_string(s: str) -> str:
    """Sanitize string for SVG"""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")
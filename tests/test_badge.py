import pytest
from src.badge import generate_badge

def test_generate_badge():
    svg = generate_badge("test", "value")
    assert "test: value" in svg
    assert "svg" in svg

def test_generate_badge_style():
    svg = generate_badge("test", "value", style="flat-square")
    assert "rx=\"3\"" in svg
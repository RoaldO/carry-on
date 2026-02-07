"""Tests for static resource loading."""

from importlib.resources import files


def test_index_html_is_packaged() -> None:
    """Verify index.html is accessible as package resource."""
    static_files = files("carry_on.static")
    content = (static_files / "index.html").read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "CarryOn" in content
    assert 'rel="icon"' in content

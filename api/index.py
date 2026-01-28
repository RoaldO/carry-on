"""Vercel entry point - wrapper for src layout compatibility.

This file exists solely to support Vercel's Python runtime which expects
the entry point at api/index.py. It adds the src directory to the Python
path and re-exports the FastAPI app from the actual module location.
"""

import sys
from pathlib import Path

# Add src directory to Python path for Vercel runtime
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Re-export the app from the actual module
from carry_on.api.index import app  # noqa: E402

__all__ = ["app"]

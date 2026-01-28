# Vercel Entry Point

This folder exists solely for Vercel deployment compatibility.

Vercel's Python runtime expects the entry point at `api/index.py`. Since this project uses a `src/carry_on` layout, the `index.py` file here is a thin wrapper that:

1. Adds the `src/` directory to the Python path
2. Re-exports the FastAPI `app` from `carry_on.api.index`

The actual application code lives in `src/carry_on/api/index.py`.

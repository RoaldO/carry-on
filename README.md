# CarryOn

Golf shot tracking web application.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: MongoDB Atlas
- **Hosting**: Vercel (serverless)
- **Package Manager**: uv

## Getting Started

```bash
# Install dependencies
uv sync --dev

# Run locally
uv run uvicorn api.index:app --port 8787

# Run tests
uv run pytest -v
```

## Development Guidelines

All contributors MUST adhere to the Architecture Decision Records (ADRs).

See the full index at [`docs/adr/README.md`](docs/adr/README.md).

Please read these ADRs before contributing to understand our development practices and architectural decisions.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | MongoDB Atlas connection string |
| `APP_PIN` | PIN for API authentication |

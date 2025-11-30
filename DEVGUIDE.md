# Developer Guide

## Project Structure

```
src/
├── badges/          # Badge generation modules
├── providers/       # Data provider modules
├── themes/          # Theme definitions
├── plugins/         # Extension plugins
├── dashboard/       # Web UI
├── analytics.py     # Usage tracking
├── cache.py         # Caching layer
├── config.py        # Configuration
├── main.py          # FastAPI app
├── scheduler.py     # Background tasks
└── utils.py         # Utilities
```

## Development Setup

1. Install dependencies: `pip install -e ".[dev]"`
2. Run tests: `pytest`
3. Start server: `uvicorn src.main:app --reload`
4. Access docs: `http://localhost:8000/docs`

## Adding a New Provider

1. Create `src/providers/new_provider.py`
2. Implement `async def get_metric(metric: str) -> str`
3. Add to main.py imports

## Adding a New Theme

1. Edit `src/themes/__init__.py`
2. Add theme definition with template, colors, etc.

## Testing

- Unit tests in `tests/`
- Run with `pytest`
- Coverage: `pytest --cov=src`

## Code Style

- Black for formatting
- Ruff for linting
- Type hints required
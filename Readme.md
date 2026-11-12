# Shortly 🔗

A tiny URL shortener REST API built with FastAPI and SQLite. It has click tracking, input validation, automatic API docs and tests.

## Features
- Create short links (POST /links)
- Redirect to the original URL (GET /{code})
- Click statistics (GET /links/{code}/stats)
- URL validation with Pydantic
- Interactive docs at /docs
- Pytest suite and GitHub Actions CI

## Run locally
1. Install: pip install -r requirements.txt
2. Start: uvicorn app.main:app --reload
3. Open: http://127.0.0.1:8000/docs

## Run tests
pip install -r requirements-dev.txt
pytest

## Project structure
- app/main.py : API routes
- app/db.py : SQLite helpers
- tests/ : pytest tests

## License
MIT

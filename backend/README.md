# FairPath Backend

Backend API for FairPath. Built with FastAPI, keeping it simple and straightforward.

## Setup

First, install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the backend directory with your config. Here's what you need:

```
OPENAI_API_KEY=your_openai_api_key_here
PORT=8000
ENV_MODE=development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Just copy that into a `.env` file and fill in your OpenAI key.

## Running Locally

Single command to start the server:

```bash
uvicorn app.main:app --reload --port 8000
```

Or if you want to use the port from your .env file:

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API docs are at `http://localhost:8000/docs` (Swagger UI)

## Running Tests

Single command to run all tests:

```bash
pytest
```

For verbose output:

```bash
pytest -v
```

### Running Tests with Coverage

Run tests with coverage report (target: 90%+):

```bash
pytest --cov=. --cov-report=html --cov-report=term --cov-fail-under=90
```

This will:
- Generate HTML coverage report in `htmlcov/` directory
- Display terminal coverage report
- Fail if coverage is below 90%

### CI/CD

Tests run automatically on:
- Push to `main`, `master`, or `develop` branches
- Pull requests to `main`, `master`, or `develop` branches

The CI pipeline:
1. Runs all tests with coverage
2. Enforces 90%+ coverage threshold
3. Uploads coverage reports (XML, HTML)
4. Optionally uploads to Codecov (if `CODECOV_TOKEN` is configured)

Coverage reports are available as GitHub Actions artifacts.

## Environment Variables

See `.env.example` for all available variables. Key ones:

- `OPENAI_API_KEY` - Required for AI features
- `PORT` - Server port (default: 8000)
- `ENV_MODE` - Environment mode: development, production, or testing
- `CORS_ORIGINS` - Comma-separated list of allowed origins for CORS
- `EAGER_LOAD_MODELS` - Set to `true` to preload models at startup (default: `false` to save memory)

### Memory Optimization

For memory-constrained environments (e.g., Render free tier with 512MB limit):
- **EAGER_LOAD_MODELS=false** (default): Models and data load lazily on first request. This saves memory at startup but adds a small delay to the first request.
- **EAGER_LOAD_MODELS=true**: Models and data preload at startup for faster first request, but uses more memory.

The production Dockerfile is configured to use 1 worker (instead of 4) to reduce memory usage, as each worker process loads models separately.

## Project Structure

```
backend/
├── app/           # Main application (FastAPI app, config)
├── routes/        # API route handlers
├── services/      # Business logic layer
├── models/        # Pydantic schemas for validation
├── data/          # Data files, database
├── artifacts/     # Generated artifacts
└── tests/         # Test files
```

## Response Format

All endpoints use a consistent response format:

**Success:**
```json
{
  "success": true,
  "message": "Operation completed",
  "data": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "message": "Error description",
  "error": "Error details",
  "details": { ... }
}
```

## Request Validation

All endpoints use Pydantic schemas for request validation. Invalid requests will return 422 with validation errors.

## CORS

CORS is configured to allow requests from:
- localhost:3000 (React default)
- localhost:5173 (Vite default)
- localhost:8080
- Any origins specified in `CORS_ORIGINS` env variable


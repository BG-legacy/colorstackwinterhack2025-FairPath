# FairPath Backend

Backend API for **colorstackwinterhack2025-fairpath**. Built with FastAPI, keeping it simple and straightforward.

Part of the FairPath project - an ethical, inclusive, and human-centered AI career recommendation system built for ColorStack Winter Hack 2025 with a focus on Responsible AI principles.

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

## Deployment

### Heroku (Recommended)

Heroku is a great platform for deploying Python applications. The backend is already configured for Heroku deployment.

#### Prerequisites

1. **Install Heroku CLI**: Download from [heroku.com](https://devcenter.heroku.com/articles/heroku-cli)
2. **Login to Heroku**:
   ```bash
   heroku login
   ```

#### Deployment Steps

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create a Heroku app** (if you haven't already):
   ```bash
   heroku create your-app-name
   ```
   Or use an existing app:
   ```bash
   heroku git:remote -a your-app-name
   ```

3. **Set environment variables** in Heroku dashboard or via CLI:
   ```bash
   heroku config:set OPENAI_API_KEY=your_openai_api_key_here
   heroku config:set ENV_MODE=production
   heroku config:set EAGER_LOAD_MODELS=false
   heroku config:set CORS_ORIGINS=https://your-frontend-url.com
   ```
   
   **Note**: `PORT` is automatically set by Heroku - don't override it.

4. **Deploy to Heroku**:
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```
   (Use `master` instead of `main` if that's your default branch)

5. **Check deployment status**:
   ```bash
   heroku logs --tail
   ```

6. **Open your app**:
   ```bash
   heroku open
   ```

#### Heroku Configuration

- **Procfile**: Already configured to run `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1`
- **runtime.txt**: Specifies Python 3.11.9
- **requirements.txt**: All dependencies are listed
- **Artifacts**: Model files and data files are included in the repository

#### Environment Variables for Heroku

Set these in the Heroku dashboard (Settings → Config Vars) or via CLI:

- `OPENAI_API_KEY` - **Required** - Your OpenAI API key
- `ENV_MODE=production` - Set to production mode
- `EAGER_LOAD_MODELS=false` - Recommended to save memory (models load on first request)
- `CORS_ORIGINS` - Your frontend URL(s), comma-separated (e.g., `https://your-frontend.vercel.app`)
- `PORT` - **Automatically set by Heroku** - Don't override this

#### Memory Optimization

For Heroku's free tier (512MB), it's recommended to:
- Set `EAGER_LOAD_MODELS=false` (default) - Models load lazily on first request
- Use 1 worker (already configured in Procfile)

#### Troubleshooting

- **View logs**: `heroku logs --tail`
- **Check app status**: `heroku ps`
- **Restart app**: `heroku restart`
- **Run commands**: `heroku run python -m pytest` (for testing)

### Render (Native Python Deployment - Alternative)

For Render, you can deploy directly without Docker to save memory:

1. **Create a new Web Service** on Render
2. **Connect your repository** and set the root directory to `backend/`
3. **Build Command**: `pip install -r requirements.txt` (or leave blank - Render auto-detects)
4. **Start Command**: Render will automatically use the `Procfile` which runs:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
   ```
5. **Environment Variables**: Set these in Render's dashboard:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `ENV_MODE=production`
   - `EAGER_LOAD_MODELS=false` (recommended for 512MB free tier)
   - `CORS_ORIGINS` - Your frontend URL(s)
   - `PORT` - Automatically set by Render (don't override)

**Note**: The `Procfile` and `runtime.txt` files are included for native Python deployment. This avoids Docker overhead and reduces memory usage.

### Docker Deployment (Alternative)

If you prefer Docker, use `Dockerfile.prod` and set the Dockerfile path in Render's settings.


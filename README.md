# colorstackwinterhack2025-fairpath

## Description

**FairPath** is an ethical, inclusive, and human-centered AI career recommendation system that helps individuals discover career paths based on their skills, interests, and work values—without relying on demographic data. Built with Responsible AI principles at its core, FairPath prioritizes fairness, accountability, transparency, and real-world impact.

FairPath addresses the critical problem of biased career recommendations that perpetuate systemic inequalities. Traditional career guidance systems often inadvertently reinforce existing disparities by considering demographic factors or lacking transparency in their decision-making processes. FairPath eliminates these biases by:

- **Excluding all demographic data** from recommendations (age, gender, race, ethnicity, etc.)
- **Providing transparent explanations** for every recommendation
- **Ensuring multiple diverse options** are always presented
- **Including confidence bands and uncertainty ranges** to set appropriate expectations
- **Offering model cards and trust panels** for full transparency

## How FairPath Aligns with Responsible AI

### 🎯 **Fairness**
- **Demographic Guardrails**: Actively rejects any demographic data in inputs, ensuring recommendations are based solely on skills, interests, and work values
- **Multiple Options**: Always provides 3-5 diverse career recommendations to prevent single-point-of-failure bias
- **Baseline Fallback**: Uses deterministic baseline ranking when ML models are unavailable, ensuring consistent and fair outcomes

### 🔍 **Transparency**
- **Explainability**: Every recommendation includes detailed explanations showing which skills contributed most and why
- **Model Cards**: Comprehensive documentation of model performance, training data, and limitations
- **Trust Panel**: Public-facing transparency dashboard showing what data is collected, how it's used, and what's excluded
- **Confidence Bands**: Recommendations include uncertainty ranges, not just point estimates

### ⚖️ **Accountability**
- **Input Validation**: Strict validation prevents demographic data from entering the system
- **Error Handling**: Graceful fallbacks ensure the system always provides recommendations, even when models fail
- **Audit Trails**: Clear logging and monitoring for system behavior
- **90%+ Test Coverage**: Comprehensive test suite ensures reliability and correctness

### 🌍 **Real-World Impact**
- **Accessible Career Guidance**: Helps individuals from all backgrounds discover career paths without bias
- **Skills-Based Matching**: Focuses on transferable skills and interests, making career transitions more accessible
- **Education Pathways**: Provides multiple pathways (traditional degree, bootcamp, certifications) to reach career goals
- **Career Switching Support**: Helps individuals transition between careers by identifying skill overlaps

## Technologies Used

### Backend
- **FastAPI** - Modern, fast Python web framework
- **Python 3.11** - Core programming language
- **scikit-learn** - Machine learning models for career recommendations
- **Pandas & NumPy** - Data processing and analysis
- **OpenAI API** - Enhanced explanations and pathway generation
- **Pydantic** - Data validation and schema management
- **pytest** - Testing framework with 90%+ coverage

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **TanStack Query (React Query)** - Data fetching and state management
- **React Hook Form + Zod** - Form validation
- **Axios** - HTTP client
- **Zustand** - State management

### Infrastructure & Deployment
- **Heroku** - Backend hosting
- **Docker** - Containerization (optional)
- **Git** - Version control

## Setup & Installation Instructions

### Prerequisites

- **Python 3.11+** (for backend)
- **Node.js 18+** and **npm** (for frontend)
- **OpenAI API Key** (for enhanced features)

### Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** in the `backend/` directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   PORT=8000
   ENV_MODE=development
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173
   EAGER_LOAD_MODELS=false
   ```

4. **Run the backend server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`
   - API docs: `http://localhost:8000/docs` (Swagger UI)

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create a `.env.local` file** (optional, for local backend):
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. **Start the development server**:
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

### Running Tests

**Backend tests** (from `backend/` directory):
```bash
pytest
```

**With coverage**:
```bash
pytest --cov=. --cov-report=html --cov-report=term --cov-fail-under=90
```

### Building for Production

**Frontend**:
```bash
cd frontend
npm run build
```

**Backend**: See deployment instructions in `backend/README.md`

## Project Structure

```
FairPath/
├── backend/              # FastAPI backend
│   ├── app/             # Main application (FastAPI app, config)
│   ├── routes/           # API route handlers
│   ├── services/         # Business logic layer
│   │   ├── guardrails_service.py    # Responsible AI guardrails
│   │   ├── recommendation_service.py # ML recommendation engine
│   │   └── ...
│   ├── models/           # Pydantic schemas
│   ├── data/             # Data files and database
│   ├── artifacts/        # ML models and generated artifacts
│   ├── tests/            # Test suite (90%+ coverage)
│   └── middleware/       # Rate limiting, size limiting
├── frontend/             # React + TypeScript frontend
│   ├── src/
│   │   ├── pages/        # Page components
│   │   ├── components/   # Reusable components
│   │   ├── api/          # API client
│   │   └── ...
│   └── ...
└── README.md             # This file
```

## Key Features

### 🛡️ Responsible AI Features
- **Demographic Guardrails**: Automatic detection and rejection of demographic data
- **Explainability**: Every recommendation includes "why" explanations
- **Trust Panel**: Transparency dashboard (`/api/trust-panel`)
- **Model Cards**: Comprehensive model documentation (`/api/model-cards`)
- **Confidence Bands**: Uncertainty ranges for all recommendations

### 🎯 Career Recommendation Features
- **Skills-Based Matching**: Match careers based on transferable skills
- **RIASEC Interests**: Incorporate Holland Code interest categories
- **Work Values**: Consider achievement, relationships, independence, etc.
- **Multiple Pathways**: Education pathways (degree, bootcamp, certifications)
- **Career Switching**: Identify skill overlaps for career transitions

### 📊 Technical Features
- **ML + Baseline Fallback**: ML model with deterministic baseline backup
- **Lazy Loading**: Memory-efficient model loading
- **Rate Limiting**: API protection against abuse
- **Comprehensive Testing**: 90%+ test coverage
- **Type Safety**: Full TypeScript + Pydantic validation

## API Endpoints

### Core Endpoints
- `POST /api/recommendations` - Get career recommendations with explainability
- `POST /api/intake/intake` - Submit user profile data
- `GET /api/trust-panel` - Transparency information
- `GET /api/model-cards` - Model documentation
- `POST /api/career-switch` - Career transition analysis
- `POST /api/paths` - Education pathway generation

See `backend/README.md` for complete API documentation.

## Team Members & Contributions

### [Your Name/Team Name]
- **Role**: [Primary Developer / Full-Stack Developer / etc.]
- **Contributions**:
  - Designed and implemented the Responsible AI guardrails system
  - Built the ML recommendation engine with explainability features
  - Developed the FastAPI backend with comprehensive test coverage
  - Created the React frontend with TypeScript
  - Implemented trust panel and model cards for transparency
  - Set up deployment infrastructure (Heroku)

*Note: Please update this section with your actual team information and contributions.*

## Additional Resources

- **Backend Documentation**: See `backend/README.md` for detailed backend setup and deployment
- **Frontend Documentation**: See `frontend/README.md` for frontend-specific details
- **API Documentation**: Available at `http://localhost:8000/docs` when backend is running

## License

[Add your license here]

## Acknowledgments

Built for **ColorStack Winter Hack 2025** with a focus on Responsible AI principles.

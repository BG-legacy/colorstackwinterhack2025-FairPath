# FairPath Frontend

React + TypeScript + Vite frontend application for **colorstackwinterhack2025-fairpath**.

Part of the FairPath project - an ethical, inclusive, and human-centered AI career recommendation system built for ColorStack Winter Hack 2025 with a focus on Responsible AI principles.

## Getting Started

### Prerequisites

- Node.js 18+ and npm (or yarn/pnpm)

### Installation

1. Install dependencies:
```bash
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Building for Production

Build the production bundle:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## Configuration

### API Base URL

The frontend is configured to connect to the backend API. By default, it uses `http://localhost:8000` for local development.

**For Production (Heroku):**
The `.env` file is configured to use the Heroku backend:
```env
VITE_API_BASE_URL=https://fairpath-01638745e0c5.herokuapp.com
```

**For Local Development:**
If you want to use a local backend, create a `.env.local` file:
```env
VITE_API_BASE_URL=http://localhost:8000
```

The `.env.example` file shows the default local development configuration.

## Project Structure

```
frontend/
├── src/
│   ├── api/           # API client configuration
│   ├── pages/         # Page components
│   ├── components/    # Reusable components
│   ├── App.tsx        # Main app component
│   ├── main.tsx       # Entry point
│   └── index.css      # Global styles
├── public/            # Static assets
├── index.html         # HTML template
└── vite.config.ts     # Vite configuration
```

## Features

- ⚡ Fast HMR (Hot Module Replacement)
- 🎯 TypeScript for type safety
- 🛣️ React Router for routing
- 🔌 Axios for API calls
- 🎨 Modern CSS styling

## Backend Integration

The frontend communicates with the FastAPI backend. 

**Production:** The frontend is configured to use the Heroku backend at `https://fairpath-01638745e0c5.herokuapp.com` (set in `.env`).

**Local Development:** The Vite dev server is configured with a proxy to forward `/api` requests to `http://localhost:8000`. Make sure the backend server is running before starting the frontend for full functionality.



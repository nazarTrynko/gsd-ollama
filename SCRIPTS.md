# Available Scripts

This document lists all available npm scripts in the root `package.json`.

## Installation

```bash
# Install all dependencies (backend + frontend)
npm run setup

# Install backend only
npm run setup:backend

# Install frontend only
npm run setup:frontend

# Install Playwright browsers
npm run install:playwright
```

## Development

```bash
# Start both backend and frontend servers
npm run dev
# or
npm start

# Start backend only (port 8000)
npm run dev:backend
# or
npm run start:backend

# Start frontend only (port 5173)
npm run dev:frontend
# or
npm run start:frontend
```

## Testing

```bash
# Run all tests (backend + frontend)
npm test

# Backend tests
npm run test:backend          # All backend tests
npm run test:backend:e2e      # E2E tests only
npm run test:backend:unit     # Unit tests only (excludes e2e)

# Frontend tests
npm run test:frontend         # Run Playwright E2E tests
npm run test:frontend:ui      # Interactive UI mode
npm run test:frontend:headed  # Run with visible browser

# E2E tests
npm run test:e2e            # Backend + frontend E2E
npm run test:e2e:full        # All E2E including full stack
npm run test:e2e:fullstack   # Full stack integration tests
```

## Building

```bash
# Build frontend for production
npm run build
# or
npm run build:frontend
```

## Linting

```bash
# Lint frontend code
npm run lint
# or
npm run lint:frontend
```

## Code Quality Checks

```bash
# Quick check (lint + unit tests)
npm run check

# Full check (lint + all tests)
npm run check:all
```

## Cleaning

```bash
# Clean build artifacts
npm run clean                 # Backend + frontend
npm run clean:backend         # Backend only
npm run clean:frontend        # Frontend only
npm run clean:all             # Everything including node_modules
```

## Script Categories

### Installation Scripts
- `install:all` - Install backend and frontend dependencies
- `install:backend` - Install backend Python dependencies
- `install:frontend` - Install frontend npm dependencies
- `install:playwright` - Install Playwright browsers
- `setup` - Full setup (install all + Playwright)
- `setup:backend` - Backend setup only
- `setup:frontend` - Frontend setup only

### Development Scripts
- `dev` - Start both servers in parallel
- `dev:backend` - Start backend server
- `dev:frontend` - Start frontend dev server
- `start` - Alias for `dev`
- `start:backend` - Alias for `dev:backend`
- `start:frontend` - Alias for `dev:frontend`

### Testing Scripts
- `test` - Run all tests
- `test:backend` - Backend tests
- `test:backend:e2e` - Backend E2E tests
- `test:backend:unit` - Backend unit tests
- `test:frontend` - Frontend E2E tests
- `test:frontend:ui` - Frontend tests in UI mode
- `test:frontend:headed` - Frontend tests with visible browser
- `test:e2e` - All E2E tests
- `test:e2e:full` - Complete E2E test suite
- `test:e2e:fullstack` - Full stack integration tests

### Build Scripts
- `build` - Build frontend
- `build:frontend` - Build frontend for production

### Lint Scripts
- `lint` - Lint frontend code
- `lint:frontend` - Lint frontend code

### Clean Scripts
- `clean` - Clean build artifacts
- `clean:backend` - Clean backend artifacts
- `clean:frontend` - Clean frontend artifacts
- `clean:all` - Clean everything

### Check Scripts
- `check` - Quick quality check
- `check:all` - Full quality check

## Examples

### First Time Setup
```bash
npm run setup
```

### Daily Development
```bash
# Start development servers
npm run dev

# In another terminal, run tests
npm test
```

### Before Committing
```bash
# Run quality checks
npm run check:all
```

### CI/CD Pipeline
```bash
# Install dependencies
npm run install:all

# Run all tests
npm test

# Build for production
npm run build
```

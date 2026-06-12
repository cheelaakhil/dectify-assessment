# SpaceToday Frontend

This is the frontend application for the SpaceToday DECTIFY Assessment. It is built with React 19, Vite, TypeScript, and React Query.

## Setup Instructions

1. Ensure you have Node.js 18+ installed.
2. Install dependencies:
   ```bash
   npm install
   ```

## Environment Variables

Currently, the frontend connects to the backend running at `http://localhost:8000/api`. This base URL is defined in `src/services/api.ts`. If you need to configure a different environment, you can modify it there or inject it via Vite environment variables.

## Run Commands

- **Development Server:**
  ```bash
  npm run dev
  ```
- **Production Build:**
  ```bash
  npm run build
  ```
- **Preview Production Build:**
  ```bash
  npm run preview
  ```

## Test Commands

The application uses Vitest and React Testing Library for tests. We use Mock Service Worker (MSW) to mock the backend during tests.

- **Run Tests with Coverage:**
  ```bash
  npm run test
  ```

## State Management Approach

1. **Server State (`@tanstack/react-query`)**: All external data from APIs (APOD, Mars photos, etc.) is managed using React Query. It handles caching, background fetching, deduplication, and loading/error states out-of-the-box.
2. **Authentication State (`AuthContext`)**: User authentication and session management is handled via React Context. The access token is stored securely in memory to prevent XSS vulnerabilities. The refresh token is managed by an HttpOnly cookie sent automatically with credentials. The API client uses an interceptor to transparently refresh the access token when a 401 response is received.
3. **Local UI State**: Simple React `useState` is used for component-level UI state like forms and toggles.

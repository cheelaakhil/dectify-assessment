import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, beforeEach } from 'vitest';
import { http, HttpResponse } from 'msw';
import { server } from '../mocks/server';
import Dashboard from './Dashboard';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const renderDashboard = () => render(
  <QueryClientProvider client={queryClient}>
    <Dashboard />
  </QueryClientProvider>
);

describe('Dashboard component', () => {
  beforeEach(() => {
    queryClient.clear();
  });

  it('renders successfully with all data', async () => {
    renderDashboard();

    expect(screen.getByText('Fetching data from NASA...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Astronomy Picture of the Day')).toBeInTheDocument();
      expect(screen.getByText('Mock APOD')).toBeInTheDocument();
    });
  });

  it('renders partial failures gracefully', async () => {
    // Force APOD and Mars to fail
    server.use(
      http.get('http://localhost:8000/api/space/dashboard', () => {
        return HttpResponse.json({
          apod: { error: 'Service unavailable: Exception' },
          mars_photos: { error: 'Service unavailable: Exception' },
          asteroids: { near_earth_objects: {} },
          earth_events: { events: [{ id: '1', title: 'Test Event' }] }
        });
      })
    );

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('APOD service unavailable')).toBeInTheDocument();
      expect(screen.getByText('Mars photos service unavailable')).toBeInTheDocument();
      expect(screen.getByText('Test Event')).toBeInTheDocument(); // Earth events still render
    });
  });
});

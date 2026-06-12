import { http, HttpResponse } from 'msw';

export const handlers = [
  http.post('http://localhost:8000/api/auth/login', () => {
    return HttpResponse.json({ access_token: 'mock-token' });
  }),

  http.post('http://localhost:8000/api/auth/refresh', () => {
    return HttpResponse.json({ access_token: 'mock-token' });
  }),

  http.post('http://localhost:8000/api/auth/signup', () => {
    return HttpResponse.json({ access_token: 'mock-token' }, { status: 201 });
  }),

  http.get('http://localhost:8000/api/auth/me', () => {
    return HttpResponse.json({ id: 1, email: 'test@example.com', name: 'Test User' });
  }),

  http.get('http://localhost:8000/api/space/dashboard', () => {
    return HttpResponse.json({
      apod: { title: 'Mock APOD', url: 'http://mock.url', explanation: 'A beautiful mock explanation of space.', media_type: 'image', date: '2026-01-01' },
      mars_photos: { photos: [] },
      asteroids: { near_earth_objects: {} },
      earth_events: { events: [] }
    });
  }),
];

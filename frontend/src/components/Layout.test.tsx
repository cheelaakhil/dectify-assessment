import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Layout from './Layout';
import { useAuth } from '../context/AuthContext';
import { describe, it, expect, vi } from 'vitest';

vi.mock('../context/AuthContext');

describe('Layout component', () => {
  it('shows loading state initially', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      isLoading: true,
      login: vi.fn(),
      signup: vi.fn(),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter>
        <Layout />
      </MemoryRouter>
    );

    expect(screen.getByText('Loading SpaceToday...')).toBeInTheDocument();
  });

  it('renders outlet when user is logged in', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: 1, name: 'Test', email: 'test@example.com' },
      isLoading: false,
      login: vi.fn(),
      signup: vi.fn(),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter>
        <Layout />
      </MemoryRouter>
    );

    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });
});

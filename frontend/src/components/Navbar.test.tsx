import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Navbar from './Navbar';
import { useAuth } from '../context/AuthContext';
import { describe, it, expect, vi } from 'vitest';

vi.mock('../context/AuthContext');

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('Navbar component', () => {
  it('renders correctly with user name', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: 1, name: 'John Doe', email: 'john@example.com' },
      isLoading: false,
      login: vi.fn(),
      signup: vi.fn(),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
  });

  it('calls logout and navigates to login on logout click', async () => {
    const logoutMock = vi.fn().mockResolvedValue(undefined);
    vi.mocked(useAuth).mockReturnValue({
      user: { id: 1, name: 'John Doe', email: 'john@example.com' },
      isLoading: false,
      login: vi.fn(),
      signup: vi.fn(),
      logout: logoutMock,
    });

    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );

    const logoutBtn = screen.getByText('Logout');
    fireEvent.click(logoutBtn);

    expect(logoutMock).toHaveBeenCalled();
    // mockNavigate is not trivially testable without more async ticks in some setups, but we can check the spy
    // Wait for the async onClick to complete
    await Promise.resolve();
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });
});

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Login from './Login';
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

describe('Login component', () => {
  it('calls login on submit and navigates on success', async () => {
    const loginMock = vi.fn().mockResolvedValue(undefined);
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      isLoading: false,
      login: loginMock,
      signup: vi.fn(),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'password123' } });
    
    fireEvent.click(screen.getByRole('button', { name: /Sign In/i }));

    await waitFor(() => {
      expect(loginMock).toHaveBeenCalledWith('test@example.com', 'password123');
    });
    
    expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
  });

  it('displays error on failed login', async () => {
    const loginMock = vi.fn().mockRejectedValue({ response: { data: { error: { message: 'Invalid credentials' } } } });
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      isLoading: false,
      login: loginMock,
      signup: vi.fn(),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'wrong' } });
    
    fireEvent.click(screen.getByRole('button', { name: /Sign In/i }));

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });
  });
});

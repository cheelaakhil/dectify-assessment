import { render, screen, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from './AuthContext';
import { describe, it, expect } from 'vitest';

const TestComponent = () => {
  const { user, isLoading } = useAuth();
  if (isLoading) return <div>Loading...</div>;
  if (!user) return <div>Not logged in</div>;
  return <div>Logged in as {user.name}</div>;
};

describe('AuthContext', () => {
  it('restores session on mount', async () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Logged in as Test User')).toBeInTheDocument();
    });
  });
});

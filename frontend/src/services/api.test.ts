import { describe, it, expect, vi, beforeEach } from 'vitest';
import api from './api';
import toast from 'react-hot-toast';

vi.mock('react-hot-toast');

describe('API Client Error Handling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should show toast error on 429 status', async () => {
    const error = {
      response: { status: 429 },
      config: { url: '/test' },
      isAxiosError: true
    };
    
    // Simulate interceptor failure manually
    try {
      // @ts-expect-error Mocking interceptor rejection
      await api.interceptors.response.handlers[0].rejected(error);
    } catch {
      // expected to reject
    }
    
    expect(toast.error).toHaveBeenCalledWith('Rate limit exceeded. Please try again later.');
  });
});

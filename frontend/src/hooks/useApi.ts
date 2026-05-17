import { useState, useCallback } from 'react';
import type { AxiosResponse } from 'axios';

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T>() {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(
    async (promise: Promise<AxiosResponse<T>>): Promise<T | null> => {
      setState({ data: null, loading: true, error: null });
      try {
        const response = await promise;
        setState({ data: response.data, loading: false, error: null });
        return response.data;
      } catch (err: any) {
        const message = err.response?.data?.detail || 'Произошла ошибка';
        setState({ data: null, loading: false, error: message });
        return null;
      }
    },
    []
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return { ...state, execute, reset };
}
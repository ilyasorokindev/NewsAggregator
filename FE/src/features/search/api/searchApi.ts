import { httpClient } from '@/shared/api/httpClient';

import type { SearchResult } from '../types';

export const searchApi = {
  search: async (query: string): Promise<SearchResult[]> => {
    const response = await httpClient.get<SearchResult[]>('/search', {
      params: { s: query },
    });
    return response.data;
  },
};

import { createAsyncThunk } from '@reduxjs/toolkit';
import { isAxiosError } from 'axios';

import { searchApi } from '../api/searchApi';

import type { SearchResult } from '../types';

const getSearchErrorMessage = (error: unknown): string => {
  if (isAxiosError(error)) {
    const data = error.response?.data;

    if (typeof data === 'string' && data.length > 0) {
      return data;
    }

    if (
      data &&
      typeof data === 'object' &&
      'message' in data &&
      typeof data.message === 'string'
    ) {
      return data.message;
    }

    if (error.response?.status === 404) {
      return 'Search service is unavailable. Please try again later.';
    }

    return error.message || 'Search failed. Please try again.';
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Search failed. Please try again.';
};

export const searchNews = createAsyncThunk<
  SearchResult[],
  string,
  { rejectValue: string }
>('search/searchNews', async (query, { rejectWithValue }) => {
  const trimmedQuery = query.trim();

  if (!trimmedQuery) {
    return rejectWithValue('Please enter a search query.');
  }

  try {
    return await searchApi.search(trimmedQuery);
  } catch (error) {
    return rejectWithValue(getSearchErrorMessage(error));
  }
});

import { createSlice } from '@reduxjs/toolkit';

import { searchNews } from './searchThunks';

import type { SearchState } from '../types';

const initialState: SearchState = {
  results: [],
  loading: false,
  error: null,
};

export const searchSlice = createSlice({
  name: 'search',
  initialState,
  reducers: {
    clearSearchError: (state) => {
      state.error = null;
    },
    resetSearch: () => initialState,
  },
  extraReducers: (builder) => {
    builder
      .addCase(searchNews.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.results = [];
      })
      .addCase(searchNews.fulfilled, (state, action) => {
        state.loading = false;
        state.results = action.payload;
      })
      .addCase(searchNews.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? 'Search failed';
      });
  },
});

export const { clearSearchError, resetSearch } = searchSlice.actions;

export const selectSearchResults = (state: { search: SearchState }) =>
  state.search.results;
export const selectSearchLoading = (state: { search: SearchState }) =>
  state.search.loading;
export const selectSearchError = (state: { search: SearchState }) =>
  state.search.error;

export const searchReducer = searchSlice.reducer;

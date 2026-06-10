import { createSlice } from '@reduxjs/toolkit';

import {
  createWebsite,
  deleteWebsite,
  loadWebsites,
  updateWebsite,
} from './settingsThunks';

import type { SettingsState } from '../types';

const initialState: SettingsState = {
  items: [],
  loading: false,
  error: null,
};

export const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    clearSettingsError: (state) => {
      state.error = null;
    },
    resetSettings: () => initialState,
  },
  extraReducers: (builder) => {
    builder
      .addCase(loadWebsites.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loadWebsites.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(loadWebsites.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? 'Failed to load websites';
      })
      .addCase(createWebsite.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createWebsite.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(createWebsite.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? 'Failed to create website';
      })
      .addCase(updateWebsite.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateWebsite.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(updateWebsite.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? 'Failed to update website';
      })
      .addCase(deleteWebsite.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteWebsite.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(deleteWebsite.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? 'Failed to delete website';
      });
  },
});

export const { clearSettingsError, resetSettings } = settingsSlice.actions;

export const selectWebsiteItems = (state: { settings: SettingsState }) =>
  state.settings.items;
export const selectSettingsLoading = (state: { settings: SettingsState }) =>
  state.settings.loading;
export const selectSettingsError = (state: { settings: SettingsState }) =>
  state.settings.error;

export const settingsReducer = settingsSlice.reducer;

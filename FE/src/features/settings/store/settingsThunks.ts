import { createAsyncThunk } from '@reduxjs/toolkit';

import { settingsApi } from '../api/settingsApi';
import { validateWebsiteUrl } from '../utils/urlValidation';

import type { WebsiteItem } from '../types';
import type { RootState } from '@/app/store';
import { getApiErrorMessage } from '@/shared/api/getApiErrorMessage';

export const loadWebsites = createAsyncThunk<
  WebsiteItem[],
  void,
  { rejectValue: string }
>('settings/loadWebsites', async (_, { rejectWithValue }) => {
  try {
    return await settingsApi.getItems();
  } catch (error) {
    return rejectWithValue(
      getApiErrorMessage(error, 'Failed to load websites. Please try again.'),
    );
  }
});

export const createWebsite = createAsyncThunk<
  void,
  string,
  { rejectValue: string; state: RootState }
>('settings/createWebsite', async (url, { rejectWithValue, dispatch }) => {
  const validationError = validateWebsiteUrl(url);

  if (validationError) {
    return rejectWithValue(validationError);
  }

  try {
    await settingsApi.createItem({ guid: '', url: url.trim() });
    void dispatch(loadWebsites());
  } catch (error) {
    return rejectWithValue(
      getApiErrorMessage(error, 'Failed to create website. Please try again.'),
    );
  }
});

export const updateWebsite = createAsyncThunk<
  void,
  WebsiteItem,
  { rejectValue: string; state: RootState }
>('settings/updateWebsite', async (item, { rejectWithValue, dispatch }) => {
  const validationError = validateWebsiteUrl(item.url);

  if (validationError) {
    return rejectWithValue(validationError);
  }

  try {
    await settingsApi.updateItem({ ...item, url: item.url.trim() });
    void dispatch(loadWebsites());
  } catch (error) {
    return rejectWithValue(
      getApiErrorMessage(error, 'Failed to update website. Please try again.'),
    );
  }
});

export const deleteWebsite = createAsyncThunk<
  void,
  string,
  { rejectValue: string; state: RootState }
>('settings/deleteWebsite', async (guid, { getState, rejectWithValue, dispatch }) => {
  const item = getState().settings.items.find((website) => website.guid === guid);

  if (!item) {
    return rejectWithValue('Website not found.');
  }

  try {
    await settingsApi.deleteItem(item);
    void dispatch(loadWebsites());
  } catch (error) {
    return rejectWithValue(
      getApiErrorMessage(error, 'Failed to delete website. Please try again.'),
    );
  }
});

import { configureStore } from '@reduxjs/toolkit';

import { searchReducer } from '@/features/search/store/searchSlice';
import { settingsReducer } from '@/features/settings/store/settingsSlice';

export const store = configureStore({
  reducer: {
    search: searchReducer,
    settings: settingsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

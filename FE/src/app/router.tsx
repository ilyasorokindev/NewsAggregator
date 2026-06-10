import { createBrowserRouter } from 'react-router-dom';

import { AppLayout } from '@/shared/components/layout/AppLayout';
import { SearchPage } from '@/features/search/pages/SearchPage';
import { SettingsPage } from '@/features/settings/pages/SettingsPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: <SearchPage />,
      },
      {
        path: 'settings',
        element: <SettingsPage />,
      },
    ],
  },
]);

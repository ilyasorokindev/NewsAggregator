import { httpClient } from '@/shared/api/httpClient';

import type { WebsiteItem } from '../types';

export const settingsApi = {
  getItems: async (): Promise<WebsiteItem[]> => {
    const response = await httpClient.get<WebsiteItem[]>('/setup/items');
    return response.data;
  },

  createItem: async (item: WebsiteItem): Promise<void> => {
    await httpClient.post('/setup/item', item);
  },

  updateItem: async (item: WebsiteItem): Promise<void> => {
    await httpClient.put('/setup/item', item);
  },

  deleteItem: async (item: WebsiteItem): Promise<void> => {
    await httpClient.delete('/setup/item', { data: item });
  },
};

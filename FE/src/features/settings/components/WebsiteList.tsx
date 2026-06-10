import { List, Typography } from '@mui/material';

import { WebsiteItem } from './WebsiteItem';

import type { WebsiteItem as WebsiteItemType } from '../types';

interface WebsiteListProps {
  items: WebsiteItemType[];
  loading: boolean;
  onEdit: (item: WebsiteItemType) => void;
  onDelete: (item: WebsiteItemType) => void;
}

export const WebsiteList = ({
  items,
  loading,
  onEdit,
  onDelete,
}: WebsiteListProps) => {
  if (items.length === 0) {
    return <Typography color="text.secondary">No websites configured</Typography>;
  }

  return (
    <List>
      {items.map((item) => (
        <WebsiteItem
          key={item.guid}
          item={item}
          disabled={loading}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </List>
  );
};

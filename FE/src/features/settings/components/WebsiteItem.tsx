import { IconButton, ListItem, ListItemText, Stack } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';

import type { WebsiteItem as WebsiteItemType } from '../types';

interface WebsiteItemProps {
  item: WebsiteItemType;
  disabled: boolean;
  onEdit: (item: WebsiteItemType) => void;
  onDelete: (item: WebsiteItemType) => void;
}

export const WebsiteItem = ({
  item,
  disabled,
  onEdit,
  onDelete,
}: WebsiteItemProps) => {
  return (
    <ListItem
      secondaryAction={
        <Stack direction="row" spacing={1}>
          <IconButton
            edge="end"
            aria-label={`edit website ${item.url}`}
            disabled={disabled}
            onClick={() => onEdit(item)}
          >
            <EditIcon />
          </IconButton>
          <IconButton
            edge="end"
            aria-label={`delete website ${item.url}`}
            disabled={disabled}
            onClick={() => onDelete(item)}
          >
            <DeleteIcon />
          </IconButton>
        </Stack>
      }
    >
      <ListItemText primary={item.url} />
    </ListItem>
  );
};

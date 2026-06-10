import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
} from '@mui/material';
import { type FormEvent } from 'react';

interface WebsiteDialogProps {
  open: boolean;
  title: string;
  url: string;
  urlError: string | null;
  loading: boolean;
  onClose: () => void;
  onSubmit: () => void;
  onUrlChange: (url: string) => void;
}

export const WebsiteDialog = ({
  open,
  title,
  url,
  urlError,
  loading,
  onClose,
  onSubmit,
  onUrlChange,
}: WebsiteDialogProps) => {
  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <form onSubmit={handleSubmit}>
        <DialogTitle>{title}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="URL"
            type="url"
            fullWidth
            required
            value={url}
            error={urlError !== null}
            helperText={urlError}
            disabled={loading}
            onChange={(event) => onUrlChange(event.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" disabled={loading}>
            Save
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from '@mui/material';

interface DeleteWebsiteDialogProps {
  open: boolean;
  url: string;
  loading: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

export const DeleteWebsiteDialog = ({
  open,
  url,
  loading,
  onClose,
  onConfirm,
}: DeleteWebsiteDialogProps) => {
  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Delete Website</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Are you sure you want to delete <strong>{url}</strong>?
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={onConfirm}
          color="error"
          variant="contained"
          disabled={loading}
        >
          Delete
        </Button>
      </DialogActions>
    </Dialog>
  );
};

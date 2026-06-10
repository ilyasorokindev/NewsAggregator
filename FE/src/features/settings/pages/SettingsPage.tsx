import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Snackbar,
  Stack,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useState } from 'react';

import { useAppDispatch, useAppSelector } from '@/app/hooks';

import { DeleteWebsiteDialog } from '../components/DeleteWebsiteDialog';
import { WebsiteDialog } from '../components/WebsiteDialog';
import { WebsiteList } from '../components/WebsiteList';
import { selectSettingsLoading, selectWebsiteItems } from '../store/settingsSlice';
import {
  createWebsite,
  deleteWebsite,
  loadWebsites,
  updateWebsite,
} from '../store/settingsThunks';
import { validateWebsiteUrl } from '../utils/urlValidation';

import type { WebsiteItem } from '../types';

type DialogMode = 'add' | 'edit' | null;

interface SnackbarState {
  open: boolean;
  message: string;
  severity: 'success' | 'error';
}

const INITIAL_SNACKBAR: SnackbarState = {
  open: false,
  message: '',
  severity: 'success',
};

export const SettingsPage = () => {
  const dispatch = useAppDispatch();
  const items = useAppSelector(selectWebsiteItems);
  const loading = useAppSelector(selectSettingsLoading);

  const [dialogMode, setDialogMode] = useState<DialogMode>(null);
  const [editingItem, setEditingItem] = useState<WebsiteItem | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<WebsiteItem | null>(null);
  const [url, setUrl] = useState('');
  const [urlError, setUrlError] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState<SnackbarState>(INITIAL_SNACKBAR);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [loadSucceeded, setLoadSucceeded] = useState(false);

  const showSnackbar = useCallback((message: string, severity: 'success' | 'error') => {
    setSnackbar({ open: true, message, severity });
  }, []);

  const closeSnackbar = () => {
    setSnackbar((current) => ({ ...current, open: false }));
  };

  const closeWebsiteDialog = () => {
    setDialogMode(null);
    setEditingItem(null);
    setUrl('');
    setUrlError(null);
  };

  const closeDeleteDialog = () => {
    setDeleteTarget(null);
  };

  useEffect(() => {
    const load = async () => {
      try {
        await dispatch(loadWebsites()).unwrap();
        setLoadSucceeded(true);
      } catch (error) {
        showSnackbar(error as string, 'error');
      } finally {
        setHasLoaded(true);
      }
    };

    void load();
  }, [dispatch, showSnackbar]);

  const handleUrlChange = (value: string) => {
    setUrl(value);
    if (urlError) {
      setUrlError(null);
    }
  };

  const handleOpenAddDialog = () => {
    setDialogMode('add');
    setEditingItem(null);
    setUrl('');
    setUrlError(null);
  };

  const handleOpenEditDialog = (item: WebsiteItem) => {
    setDialogMode('edit');
    setEditingItem(item);
    setUrl(item.url);
    setUrlError(null);
  };

  const handleOpenDeleteDialog = (item: WebsiteItem) => {
    setDeleteTarget(item);
  };

  const handleWebsiteDialogSubmit = async () => {
    const validationError = validateWebsiteUrl(url);

    if (validationError) {
      setUrlError(validationError);
      return;
    }

    try {
      if (dialogMode === 'add') {
        await dispatch(createWebsite(url)).unwrap();
        showSnackbar('Added successfully', 'success');
      } else if (dialogMode === 'edit' && editingItem) {
        await dispatch(updateWebsite({ ...editingItem, url })).unwrap();
        showSnackbar('Updated successfully', 'success');
      }

      closeWebsiteDialog();
    } catch (error) {
      showSnackbar(error as string, 'error');
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) {
      return;
    }

    try {
      await dispatch(deleteWebsite(deleteTarget.guid)).unwrap();
      showSnackbar('Deleted successfully', 'success');
      closeDeleteDialog();
    } catch (error) {
      showSnackbar(error as string, 'error');
    }
  };

  const isWebsiteDialogOpen = dialogMode !== null;
  const websiteDialogTitle = dialogMode === 'add' ? 'Add Website' : 'Edit Website';

  return (
    <Stack spacing={3}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h4" component="h1">
          Settings
        </Typography>
        <Button variant="contained" disabled={loading} onClick={handleOpenAddDialog}>
          Add Website
        </Button>
      </Stack>

      {loading && !hasLoaded && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress aria-label="Loading websites" />
        </Box>
      )}

      {loadSucceeded && (
        <WebsiteList
          items={items}
          loading={loading}
          onEdit={handleOpenEditDialog}
          onDelete={handleOpenDeleteDialog}
        />
      )}

      {loading && hasLoaded && (
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <CircularProgress size={24} aria-label="Saving changes" />
        </Box>
      )}

      <WebsiteDialog
        open={isWebsiteDialogOpen}
        title={websiteDialogTitle}
        url={url}
        urlError={urlError}
        loading={loading}
        onClose={closeWebsiteDialog}
        onSubmit={() => void handleWebsiteDialogSubmit()}
        onUrlChange={handleUrlChange}
      />

      <DeleteWebsiteDialog
        open={deleteTarget !== null}
        url={deleteTarget?.url ?? ''}
        loading={loading}
        onClose={closeDeleteDialog}
        onConfirm={() => void handleDeleteConfirm()}
      />

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={closeSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={closeSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Stack>
  );
};

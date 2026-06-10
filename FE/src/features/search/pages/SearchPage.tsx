import { Alert, Box, CircularProgress, Stack, Typography } from '@mui/material';
import { useState } from 'react';

import { useAppDispatch, useAppSelector } from '@/app/hooks';

import { SearchForm } from '../components/SearchForm';
import { SearchResults } from '../components/SearchResults';
import {
  selectSearchError,
  selectSearchLoading,
  selectSearchResults,
} from '../store/searchSlice';
import { searchNews } from '../store/searchThunks';

export const SearchPage = () => {
  const dispatch = useAppDispatch();
  const results = useAppSelector(selectSearchResults);
  const loading = useAppSelector(selectSearchLoading);
  const error = useAppSelector(selectSearchError);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = (query: string) => {
    setHasSearched(true);
    void dispatch(searchNews(query));
  };

  return (
    <Stack spacing={3}>
      <Typography variant="h4" component="h1">
        Search
      </Typography>
      <SearchForm loading={loading} onSearch={handleSearch} />
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress aria-label="Searching news" />
        </Box>
      )}
      {!loading && error && (
        <Alert severity="error" role="alert">
          {error}
        </Alert>
      )}
      {!loading && !error && (
        <SearchResults results={results} hasSearched={hasSearched} />
      )}
    </Stack>
  );
};

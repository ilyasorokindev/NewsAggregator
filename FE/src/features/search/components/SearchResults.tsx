import { Stack, Typography } from '@mui/material';

import { SearchResultCard } from './SearchResultCard';

import type { SearchResult } from '../types';

interface SearchResultsProps {
  results: SearchResult[];
  hasSearched: boolean;
}

export const SearchResults = ({ results, hasSearched }: SearchResultsProps) => {
  if (!hasSearched) {
    return null;
  }

  if (results.length === 0) {
    return <Typography color="text.secondary">No news found</Typography>;
  }

  return (
    <Stack spacing={2}>
      {results.map((result) => (
        <SearchResultCard key={result.guid} result={result} />
      ))}
    </Stack>
  );
};

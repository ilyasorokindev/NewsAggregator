import { Paper, Typography } from '@mui/material';

import type { SearchResult } from '../types';

interface SearchResultCardProps {
  result: SearchResult;
}

export const SearchResultCard = ({ result }: SearchResultCardProps) => {
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="body1">{result.text}</Typography>
    </Paper>
  );
};

import { Button, Stack, TextField } from '@mui/material';
import { type FormEvent, useState } from 'react';

interface SearchFormProps {
  loading: boolean;
  onSearch: (query: string) => void;
}

export const SearchForm = ({ loading, onSearch }: SearchFormProps) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    onSearch(query);
  };

  return (
    <Stack component="form" direction="row" spacing={2} onSubmit={handleSubmit}>
      <TextField
        label="Search news"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        fullWidth
        size="small"
        disabled={loading}
      />
      <Button type="submit" variant="contained" disabled={loading}>
        Search
      </Button>
    </Stack>
  );
};

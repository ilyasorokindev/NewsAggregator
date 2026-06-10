export interface SearchResult {
  guid: string;
  text: string;
}

export interface SearchState {
  results: SearchResult[];
  loading: boolean;
  error: string | null;
}

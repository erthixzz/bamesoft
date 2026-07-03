export type SearchType = 'equipment' | 'case' | 'user' | 'sector' | 'clinic';

export interface SearchResult {
  type: SearchType;
  id: string;
  title: string;
  subtitle?: string | null;
}

export interface SearchOut {
  results: SearchResult[];
  total: number;
}

export interface WebsiteItem {
  guid: string;
  url: string;
}

export interface SettingsState {
  items: WebsiteItem[];
  loading: boolean;
  error: string | null;
}

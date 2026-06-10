const isValidUrl = (url: string): boolean => {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
};

export const validateWebsiteUrl = (url: string): string | null => {
  const trimmed = url.trim();

  if (!trimmed) {
    return 'URL is required.';
  }

  if (!isValidUrl(trimmed)) {
    return 'Please enter a valid URL.';
  }

  return null;
};

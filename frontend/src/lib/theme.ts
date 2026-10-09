import { createContext, useContext } from 'react';

/**
 * Light, dark or the system's choice, kept in localStorage. The `dark` class
 * on <html> switches the CSS variables in index.css; an inline script in
 * index.html applies it before the first paint. The provider is
 * `components/layout/ThemeProvider`.
 */
export type Theme = 'light' | 'dark' | 'system';

export const THEME_STORAGE_KEY = 'theme';

export interface ThemeState {
  theme: Theme;
  resolvedTheme: 'light' | 'dark';
  setTheme: (theme: Theme) => void;
}

export const ThemeContext = createContext<ThemeState>({
  theme: 'system',
  resolvedTheme: 'light',
  setTheme: () => undefined,
});

export function useTheme(): ThemeState {
  return useContext(ThemeContext);
}

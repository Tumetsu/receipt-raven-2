import { Monitor, Moon, Sun } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { useTheme } from '@/lib/theme';

const NEXT = { system: 'light', light: 'dark', dark: 'system' } as const;
const LABEL = { system: 'Theme: system', light: 'Theme: light', dark: 'Theme: dark' } as const;

/** Cycles system → light → dark. */
export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const current = theme;
  const Icon = current === 'light' ? Sun : current === 'dark' ? Moon : Monitor;

  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label={LABEL[current]}
      title={LABEL[current]}
      onClick={() => setTheme(NEXT[current])}
    >
      <Icon />
    </Button>
  );
}

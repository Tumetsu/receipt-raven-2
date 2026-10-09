import { Check, ChevronsUpDown, Plus } from 'lucide-react';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { cn } from '@/lib/utils';

/**
 * A searchable select. With `allowCustom`, a value not in `options` can be
 * typed and used, so the options act as suggestions.
 */
export function Combobox({
  id,
  label,
  value,
  onChange,
  options,
  placeholder = 'Select…',
  allowCustom = false,
  invalid = false,
  disabled = false,
}: {
  id?: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: readonly string[];
  placeholder?: string;
  allowCustom?: boolean;
  invalid?: boolean;
  disabled?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const typed = search.trim();
  const offerCustom = allowCustom && typed !== '' && !options.some((option) => option === typed);

  const choose = (next: string) => {
    onChange(next);
    setSearch('');
    setOpen(false);
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          id={id}
          type="button"
          variant="outline"
          role="combobox"
          aria-label={label}
          aria-expanded={open}
          aria-invalid={invalid || undefined}
          disabled={disabled}
          className={cn(
            'bg-background dark:bg-input/30 w-full justify-between px-3 font-normal',
            !value && 'text-muted-foreground'
          )}
        >
          <span className="truncate">{value || placeholder}</span>
          <ChevronsUpDown className="opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-(--radix-popover-trigger-width) min-w-64 p-0" align="start">
        <Command>
          <CommandInput
            placeholder="Search…"
            value={search}
            onValueChange={setSearch}
            aria-label={`Search ${label.toLowerCase()}`}
          />
          <CommandList>
            <CommandEmpty>{allowCustom ? 'Type to add a new one.' : 'No matches.'}</CommandEmpty>
            {offerCustom && (
              <CommandGroup>
                <CommandItem value={`__custom__${typed}`} onSelect={() => choose(typed)}>
                  <Plus />
                  Use “{typed}”
                </CommandItem>
              </CommandGroup>
            )}
            <CommandGroup>
              {options.map((option) => (
                <CommandItem key={option} value={option} onSelect={() => choose(option)}>
                  <Check className={cn(option === value ? 'opacity-100' : 'opacity-0')} />
                  <span className="truncate">{option}</span>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}

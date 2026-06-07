import { useNavigate } from '@tanstack/react-router';
import { type KeyboardEvent, useEffect, useId, useRef, useState } from 'react';
import { useIntl } from 'react-intl';
import type { SearchResult } from '@/api/types';
import { StatusBadge } from '@/components/ui';
import { Search } from '@/components/ui/icons';
import { cn } from '@/lib/cn';
import { useSearch } from './useSearch';

/**
 * Global search overlay (DRD §11.1 / PRD §12.1). Header input + ⌘K shortcut; a
 * dropdown of up to ~8 ranked results (title with match highlight, project,
 * status). Keyboard: ↑/↓ to move, Enter to open, Esc to dismiss.
 */
const MAX_RESULTS = 8;

export function SearchOverlay() {
  const intl = useIntl();
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const listId = useId();
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);

  const { data, query: settled } = useSearch(query);
  const results = (data?.results ?? []).slice(0, MAX_RESULTS);
  const showDropdown = open && settled.length > 0;

  // ⌘K / Ctrl+K focuses the search box from anywhere.
  useEffect(() => {
    const onKey = (e: globalThis.KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  function go(result: SearchResult) {
    setOpen(false);
    setQuery('');
    navigate({
      to: '/projects/$projectId/tasks/$taskId',
      params: { projectId: result.project.id, taskId: result.task_id },
    });
  }

  function onKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Escape') {
      setOpen(false);
      inputRef.current?.blur();
      return;
    }
    if (!showDropdown) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActive((i) => (i + 1) % results.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActive((i) => (i - 1 + results.length) % results.length);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const picked = results[active];
      if (picked) go(picked);
    }
  }

  return (
    <div className="relative w-[260px]">
      <Search
        size={15}
        strokeWidth={2}
        className="pointer-events-none absolute inset-y-0 start-2.5 my-auto text-text-tertiary"
      />
      <input
        ref={inputRef}
        type="text"
        role="combobox"
        aria-expanded={showDropdown}
        aria-controls={listId}
        aria-label={intl.formatMessage({ id: 'search.label' })}
        placeholder={intl.formatMessage({ id: 'search.placeholder' })}
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
          setActive(0);
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 120)}
        onKeyDown={onKeyDown}
        className="w-full rounded-sm border border-border bg-bg-surface py-[7px] ps-8 pe-10 text-[13px] text-text-primary placeholder:text-text-tertiary focus-visible:border-primary focus-visible:bg-bg-card focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-primary"
      />
      <kbd className="pointer-events-none absolute inset-y-0 end-2 my-auto h-fit text-[11px] text-text-tertiary">
        ⌘K
      </kbd>

      {showDropdown ? (
        <div
          id={listId}
          role="listbox"
          aria-label={intl.formatMessage({ id: 'search.label' })}
          className="absolute end-0 mt-1 max-h-80 w-80 overflow-y-auto rounded-md border border-border bg-bg-card py-1 shadow-dropdown"
        >
          {results.length === 0 ? (
            <p className="px-3 py-2 text-[13px] text-text-secondary">
              {intl.formatMessage({ id: 'search.empty' })}
            </p>
          ) : (
            results.map((result, i) => (
              <button
                key={result.task_id}
                type="button"
                role="option"
                aria-selected={i === active}
                onMouseDown={(e) => {
                  e.preventDefault();
                  go(result);
                }}
                className={cn(
                  'flex w-full items-center gap-2 px-3 py-2 text-start',
                  i === active && 'bg-bg-hover',
                )}
              >
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-[13px] text-text-primary">
                    <Highlight text={result.title} query={settled} />
                  </span>
                  <span className="block truncate text-[11px] text-text-tertiary">
                    {result.project.name}
                  </span>
                </span>
                <StatusBadge status={result.status} />
              </button>
            ))
          )}
        </div>
      ) : null}
    </div>
  );
}

/** Highlight the first case-insensitive match of `query` within `text`. */
function Highlight({ text, query }: { text: string; query: string }) {
  const idx = text.toLowerCase().indexOf(query.toLowerCase());
  if (idx < 0 || query.length === 0) return <>{text}</>;
  return (
    <>
      {text.slice(0, idx)}
      <mark className="bg-primary-light text-primary">{text.slice(idx, idx + query.length)}</mark>
      {text.slice(idx + query.length)}
    </>
  );
}

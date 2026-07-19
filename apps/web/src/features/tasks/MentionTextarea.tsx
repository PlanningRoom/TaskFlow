import { type KeyboardEvent, useRef, useState } from 'react';
import type { UserSummary } from '@/api/types';
import { Avatar, Textarea } from '@/components/ui';
import { mentionHandle } from '@/lib/mentions';

/**
 * Comment textarea with @mention autocomplete (DRD §11.4). Typing `@` opens a
 * member typeahead; selecting inserts the backend handle format (display name
 * lowercased, spaces → hyphens — see services/mentions.py). Keyboard: ↑/↓ move,
 * Enter/Tab accept, Esc dismiss.
 */
export { mentionHandle };

const MENTION_RE = /(^|\s)@([A-Za-z0-9_-]*)$/;

export function MentionTextarea({
  value,
  onChange,
  members,
  placeholder,
  id,
}: {
  value: string;
  onChange: (value: string) => void;
  members: UserSummary[];
  placeholder?: string;
  id?: string;
}) {
  const ref = useRef<HTMLTextAreaElement>(null);
  const [query, setQuery] = useState<string | null>(null);
  const [active, setActive] = useState(0);

  const matches =
    query === null
      ? []
      : members
          .filter((m) => mentionHandle(m.display_name).includes(query.toLowerCase()))
          .slice(0, 6);

  function refreshQuery(text: string, caret: number) {
    const before = text.slice(0, caret);
    const match = before.match(MENTION_RE);
    setQuery(match ? (match[2] ?? null) : null);
    setActive(0);
  }

  function handleChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    onChange(e.target.value);
    refreshQuery(e.target.value, e.target.selectionStart ?? e.target.value.length);
  }

  function insert(member: UserSummary) {
    const el = ref.current;
    const caret = el?.selectionStart ?? value.length;
    const before = value.slice(0, caret);
    const after = value.slice(caret);
    const replaced = before.replace(
      MENTION_RE,
      (_m, pre: string) => `${pre}@${mentionHandle(member.display_name)} `,
    );
    onChange(replaced + after);
    setQuery(null);
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (query === null || matches.length === 0) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActive((i) => (i + 1) % matches.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActive((i) => (i - 1 + matches.length) % matches.length);
    } else if (e.key === 'Enter' || e.key === 'Tab') {
      e.preventDefault();
      const picked = matches[active];
      if (picked) insert(picked);
    } else if (e.key === 'Escape') {
      setQuery(null);
    }
  }

  return (
    <div className="relative">
      <Textarea
        ref={ref}
        id={id}
        value={value}
        placeholder={placeholder}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
      />
      {query !== null && matches.length > 0 ? (
        <ul className="absolute z-10 mt-1 w-full overflow-hidden rounded-md border border-border bg-bg-card shadow-dropdown">
          {matches.map((member, i) => (
            <li key={member.id}>
              <button
                type="button"
                onMouseDown={(e) => {
                  e.preventDefault();
                  insert(member);
                }}
                className={
                  i === active
                    ? 'flex w-full items-center gap-2 bg-bg-hover px-3 py-1.5 text-start text-[13px]'
                    : 'flex w-full items-center gap-2 px-3 py-1.5 text-start text-[13px] hover:bg-bg-hover'
                }
              >
                <Avatar
                  size="sm"
                  initials={member.initials}
                  color={member.avatar_color}
                  id={member.id}
                />
                {member.display_name ?? 'Unknown'}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}

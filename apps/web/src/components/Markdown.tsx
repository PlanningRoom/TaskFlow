import { useMemo } from 'react';
import ReactMarkdown, { type Components, type Options } from 'react-markdown';
import rehypeSanitize, { defaultSchema } from 'rehype-sanitize';
import remarkGfm from 'remark-gfm';
import type { UserSummary } from '@/api/types';
import { cn } from '@/lib/cn';
import { MENTION_URL, mentionHandle, remarkMentions } from '@/lib/mentions';

/**
 * Safe Markdown renderer (ADR 060 / TDD §6.6) for task descriptions and
 * comments: `remark-gfm` for tables/strikethrough/task-lists, `rehype-sanitize`
 * with a strict allowlist (no raw HTML/script), and every link forced to
 * `target="_blank"` + `rel="noopener noreferrer nofollow"`.
 *
 * Pass `mentions` (the DTO's resolved members) to render their `@handle`
 * tokens as teal chips; without it, mentions stay plain text.
 */
const schema = {
  ...defaultSchema,
  attributes: {
    ...defaultSchema.attributes,
    a: [...(defaultSchema.attributes?.a ?? []), 'href'],
  },
};

const components: Components = {
  a: ({ children, href }) =>
    href === MENTION_URL ? (
      <span className="rounded bg-primary-light px-1 py-0.5 font-medium text-primary">
        {children}
      </span>
    ) : (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer nofollow"
        className="text-primary underline"
      >
        {children}
      </a>
    ),
};

export function Markdown({
  children,
  className,
  mentions,
}: {
  children: string;
  className?: string;
  mentions?: UserSummary[];
}) {
  const remarkPlugins = useMemo<NonNullable<Options['remarkPlugins']>>(() => {
    const handles = new Set(
      (mentions ?? []).map((m) => mentionHandle(m.display_name)).filter(Boolean),
    );
    return handles.size > 0 ? [remarkGfm, [remarkMentions, { handles }]] : [remarkGfm];
  }, [mentions]);

  return (
    <div
      className={cn(
        'space-y-2 break-words text-[13px] leading-relaxed text-text-on-surface [&_code]:rounded [&_code]:bg-bg-surface [&_code]:px-1 [&_code]:py-0.5 [&_li]:ms-4 [&_ol]:list-decimal [&_ul]:list-disc',
        className,
      )}
    >
      <ReactMarkdown
        remarkPlugins={remarkPlugins}
        rehypePlugins={[[rehypeSanitize, schema]]}
        components={components}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}

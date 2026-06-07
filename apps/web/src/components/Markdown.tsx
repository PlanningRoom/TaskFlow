import ReactMarkdown, { type Components } from 'react-markdown';
import rehypeSanitize, { defaultSchema } from 'rehype-sanitize';
import remarkGfm from 'remark-gfm';
import { cn } from '@/lib/cn';

/**
 * Safe Markdown renderer (ADR 060 / TDD §6.6) for task descriptions and
 * comments: `remark-gfm` for tables/strikethrough/task-lists, `rehype-sanitize`
 * with a strict allowlist (no raw HTML/script), and every link forced to
 * `target="_blank"` + `rel="noopener noreferrer nofollow"`.
 *
 * `@handle` mentions render as plain text here; the comment list highlights
 * them around this component (the resolved members are on the DTO).
 */
const schema = {
  ...defaultSchema,
  attributes: {
    ...defaultSchema.attributes,
    a: [...(defaultSchema.attributes?.a ?? []), 'href'],
  },
};

const components: Components = {
  a: ({ children, href }) => (
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

export function Markdown({ children, className }: { children: string; className?: string }) {
  return (
    <div
      className={cn(
        'space-y-2 break-words text-[13px] leading-relaxed text-text-on-surface [&_code]:rounded [&_code]:bg-bg-surface [&_code]:px-1 [&_code]:py-0.5 [&_li]:ms-4 [&_ol]:list-decimal [&_ul]:list-disc',
        className,
      )}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[[rehypeSanitize, schema]]}
        components={components}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}

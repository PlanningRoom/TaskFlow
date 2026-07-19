/**
 * @mention helpers shared by the composer (MentionTextarea) and the renderer
 * (Markdown). The handle format mirrors the backend parser
 * (services/mentions.py): display name lowercased, spaces → hyphens.
 */

export function mentionHandle(displayName: string | null | undefined): string {
  return (displayName ?? '').toLowerCase().trim().replace(/\s+/g, '-');
}

/**
 * Sentinel href for mention "links". The remark plugin below wraps resolved
 * `@handle` tokens in link nodes with this URL — links survive the
 * rehype-sanitize allowlist — and the Markdown component renders them as teal
 * chips instead of anchors.
 */
export const MENTION_URL = '#mention';

const MENTION_TOKEN_RE = /@([A-Za-z0-9_-]+)/g;

type MdNode = {
  type: string;
  value?: string;
  url?: string;
  children?: MdNode[];
};

/**
 * remark plugin: turn `@handle` tokens whose handle matches a resolved member
 * into mention link nodes. Only plain text nodes are touched — code spans and
 * fenced blocks keep their literal text, and existing links are left alone.
 */
export function remarkMentions(options: { handles: ReadonlySet<string> }) {
  const { handles } = options;

  function splitMentions(value: string): MdNode[] {
    const out: MdNode[] = [];
    let last = 0;
    for (const match of value.matchAll(MENTION_TOKEN_RE)) {
      const [token, handle] = match;
      const index = match.index ?? 0;
      // Same boundary rule as the composer: a mention starts the string or
      // follows whitespace (so user@example.com never chips).
      const boundary = index === 0 || /\s/.test(value[index - 1] ?? '');
      if (!boundary || !handle || !handles.has(handle.toLowerCase())) continue;
      if (index > last) out.push({ type: 'text', value: value.slice(last, index) });
      out.push({ type: 'link', url: MENTION_URL, children: [{ type: 'text', value: token }] });
      last = index + token.length;
    }
    if (out.length === 0) return [{ type: 'text', value }];
    if (last < value.length) out.push({ type: 'text', value: value.slice(last) });
    return out;
  }

  function visit(node: MdNode) {
    if (!node.children || node.type === 'link' || node.type === 'linkReference') return;
    const next: MdNode[] = [];
    for (const child of node.children) {
      if (child.type === 'text' && typeof child.value === 'string') {
        next.push(...splitMentions(child.value));
      } else {
        visit(child);
        next.push(child);
      }
    }
    node.children = next;
  }

  return (tree: MdNode) => {
    if (handles.size > 0) visit(tree);
  };
}

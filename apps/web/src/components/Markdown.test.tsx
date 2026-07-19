import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import type { UserSummary } from '@/api/types';
import { axe } from '@/test/axe';
import { Markdown } from './Markdown';

const grace: UserSummary = {
  id: 'u2',
  display_name: 'Grace Hopper',
  initials: 'GH',
  avatar_color: 'emerald',
  deleted: false,
};

describe('Markdown mentions', () => {
  it('renders a resolved @handle as a chip, not a link', async () => {
    const { getByText, container } = render(
      <Markdown mentions={[grace]}>Nice catch @grace-hopper — shipping it.</Markdown>,
    );
    const chip = getByText('@grace-hopper');
    expect(chip.tagName).toBe('SPAN');
    expect(chip.className).toContain('text-primary');
    expect(container.querySelector('a')).toBeNull();
    expect(await axe(container)).toHaveNoViolations();
  });

  it('leaves unresolved handles and emails as plain text', () => {
    const { getByText, queryByText } = render(
      <Markdown mentions={[grace]}>Ping @nobody or mail grace@grace-hopper.dev</Markdown>,
    );
    expect(getByText(/Ping @nobody/)).toBeInTheDocument();
    // The email's "@grace-hopper" must not become a chip (no word boundary).
    expect(queryByText('@grace-hopper')).toBeNull();
  });

  it('does not chip mentions inside code spans', () => {
    const { container } = render(<Markdown mentions={[grace]}>{'`@grace-hopper`'}</Markdown>);
    const code = container.querySelector('code');
    expect(code?.textContent).toBe('@grace-hopper');
    expect(container.querySelector('span.text-primary, [class*="bg-primary-light"]')).toBeNull();
  });

  it('renders mentions as plain text when no mention list is supplied', () => {
    const { getByText } = render(<Markdown>Hey @grace-hopper</Markdown>);
    const text = getByText(/Hey @grace-hopper/);
    expect(text.querySelector('span')).toBeNull();
  });

  it('keeps real links working alongside mentions', () => {
    const { getByRole, getByText } = render(
      <Markdown mentions={[grace]}>{'See [docs](https://example.com) @grace-hopper'}</Markdown>,
    );
    const link = getByRole('link', { name: 'docs' });
    expect(link).toHaveAttribute('href', 'https://example.com');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer nofollow');
    expect(getByText('@grace-hopper').tagName).toBe('SPAN');
  });
});

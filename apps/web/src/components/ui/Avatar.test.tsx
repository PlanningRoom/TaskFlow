import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { axe } from '@/test/axe';
import { Avatar, colorClassForId } from './Avatar';

describe('Avatar', () => {
  it('maps the API palette name to the DRD token class', () => {
    const { getByRole } = render(<Avatar initials="SC" color="indigo" />);
    expect(getByRole('img')).toHaveClass('bg-avatar-purple');
  });

  it('falls back to a deterministic color from id', () => {
    const a = colorClassForId('user-1');
    const b = colorClassForId('user-1');
    expect(a).toBe(b);
    expect(a).toMatch(/^bg-avatar-/);
  });

  it('exposes an accessible label', () => {
    const { getByRole } = render(<Avatar initials="JD" label="Jane Doe" />);
    expect(getByRole('img', { name: 'Jane Doe' })).toBeInTheDocument();
  });

  it('has no axe violations across sizes', async () => {
    const { container } = render(
      <div>
        <Avatar initials="A" size="sm" color="rose" />
        <Avatar initials="B" size="md" color="emerald" />
        <Avatar initials="C" size="lg" id="x9" />
      </div>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});

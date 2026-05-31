import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { axe } from '@/test/axe';
import { Button } from './Button';

describe('Button', () => {
  it('renders each variant with no axe violations', async () => {
    const { container } = render(
      <div>
        <Button variant="primary">Primary</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="destructive">Delete</Button>
        <Button size="sm">Small</Button>
        <Button disabled>Disabled</Button>
      </div>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it('defaults to type="button" and fires onClick', async () => {
    const onClick = vi.fn();
    const { getByRole } = render(<Button onClick={onClick}>Go</Button>);
    const btn = getByRole('button', { name: 'Go' });
    expect(btn).toHaveAttribute('type', 'button');
    await userEvent.click(btn);
    expect(onClick).toHaveBeenCalledOnce();
  });

  it('does not fire when disabled', async () => {
    const onClick = vi.fn();
    const { getByRole } = render(
      <Button disabled onClick={onClick}>
        Nope
      </Button>,
    );
    await userEvent.click(getByRole('button'));
    expect(onClick).not.toHaveBeenCalled();
  });
});

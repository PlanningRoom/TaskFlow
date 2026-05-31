import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { axe } from '@/test/axe';
import { FormLabel, Input, Select, Textarea } from './Input';

describe('form inputs', () => {
  it('associates labels and has no axe violations', async () => {
    const { container, getByLabelText } = render(
      <form>
        <FormLabel htmlFor="email">Email address</FormLabel>
        <Input id="email" type="email" placeholder="you@company.com" />
        <FormLabel htmlFor="desc">Description</FormLabel>
        <Textarea id="desc" placeholder="Details" />
        <FormLabel htmlFor="assignee">Assignee</FormLabel>
        <Select id="assignee">
          <option>Unassigned</option>
        </Select>
      </form>,
    );
    expect(getByLabelText('Email address')).toBeInTheDocument();
    expect(getByLabelText('Description').tagName).toBe('TEXTAREA');
    expect(getByLabelText('Assignee').tagName).toBe('SELECT');
    expect(await axe(container)).toHaveNoViolations();
  });

  it('accepts typed input', async () => {
    const { getByLabelText } = render(
      <>
        <FormLabel htmlFor="t">Title</FormLabel>
        <Input id="t" />
      </>,
    );
    const input = getByLabelText('Title');
    await userEvent.type(input, 'Ship it');
    expect(input).toHaveValue('Ship it');
  });

  it('reflects aria-invalid', () => {
    const { getByLabelText } = render(
      <>
        <FormLabel htmlFor="e">Email</FormLabel>
        <Input id="e" aria-invalid />
      </>,
    );
    expect(getByLabelText('Email')).toHaveAttribute('aria-invalid', 'true');
  });
});

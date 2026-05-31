import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { axe } from '@/test/axe';
import { FormError, FormField } from './FormField';

describe('FormField', () => {
  it('associates label and input and has no axe violations', async () => {
    const { container, getByLabelText } = render(
      <form>
        <FormField label="Email" type="email" />
      </form>,
    );
    expect(getByLabelText('Email')).toHaveAttribute('type', 'email');
    expect(await axe(container)).toHaveNoViolations();
  });

  it('wires aria-invalid + aria-describedby to the error when present', () => {
    const { getByLabelText, getByText } = render(<FormField label="Password" error="Too short" />);
    const input = getByLabelText('Password');
    const error = getByText('Too short');
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(input).toHaveAttribute('aria-describedby', error.id);
  });

  it('omits aria-invalid when there is no error', () => {
    const { getByLabelText } = render(<FormField label="Name" />);
    expect(getByLabelText('Name')).not.toHaveAttribute('aria-invalid');
  });

  it('renders a form-level error as an alert', () => {
    const { getByRole } = render(<FormError message="Invalid email or password." />);
    expect(getByRole('alert')).toHaveTextContent('Invalid email or password.');
  });
});

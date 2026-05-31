import { forwardRef, useId } from 'react';
import { FormLabel, Input } from '@/components/ui';

interface FormFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  /** Visible label text (already localized by the caller). */
  label: string;
  /** Validation message to show below the field; absence means "valid". */
  error?: string;
}

/**
 * Label + Input + inline error, wired for accessibility: the error is given an
 * id referenced by `aria-describedby` and the input gets `aria-invalid` so the
 * DRD §7.2 error border shows. Spreads remaining props (incl. React Hook Form's
 * `register()` output) onto the input. Reused by every Phase G1 auth form.
 */
export const FormField = forwardRef<HTMLInputElement, FormFieldProps>(
  ({ label, error, id, ...props }, ref) => {
    const generatedId = useId();
    const fieldId = id ?? generatedId;
    const errorId = `${fieldId}-error`;
    return (
      <div className="mb-[18px]">
        <FormLabel htmlFor={fieldId}>{label}</FormLabel>
        <Input
          ref={ref}
          id={fieldId}
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? errorId : undefined}
          {...props}
        />
        {error ? (
          <p id={errorId} className="mt-1.5 text-[13px] text-semantic-error">
            {error}
          </p>
        ) : null}
      </div>
    );
  },
);
FormField.displayName = 'FormField';

/** Form-level error banner (e.g. login's generic "Invalid email or password."). */
export function FormError({ message }: { message: string }) {
  return (
    <p role="alert" className="mb-4 text-[13px] text-semantic-error">
      {message}
    </p>
  );
}

import { FormattedMessage } from 'react-intl';

/**
 * Generic placeholder for a not-yet-built screen (Part G fills these in). It
 * confirms the route resolved and the shell context is correct. `title` doubles
 * as the screen name shown in the content area.
 */
export function PlaceholderPage({ title, note }: { title: string; note?: string }) {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold text-text-primary">{title}</h1>
      <p className="mt-2 text-sm text-text-secondary">
        {note ?? <FormattedMessage id="app.screenComingSoon" />}
      </p>
    </div>
  );
}

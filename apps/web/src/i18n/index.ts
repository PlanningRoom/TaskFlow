import en from './locales/en.json';

/**
 * i18n configuration (ADR 061). English is the only locale at v1; the message
 * catalog is a flat id → string map consumed by react-intl's IntlProvider.
 * Additional locales are added by dropping sibling JSON files under `locales/`
 * and selecting them here.
 */
export const DEFAULT_LOCALE = 'en';

export const messagesByLocale: Record<string, Record<string, string>> = {
  en,
};

export type Locale = keyof typeof messagesByLocale;

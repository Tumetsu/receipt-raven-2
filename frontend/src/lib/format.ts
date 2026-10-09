/** Formatting and parsing of the values the UI shows, in the Finnish locale. */

const LOCALE = 'fi-FI';

const currency = new Intl.NumberFormat(LOCALE, { style: 'currency', currency: 'EUR' });
const dateFormat = new Intl.DateTimeFormat(LOCALE, {
  day: 'numeric',
  month: 'numeric',
  year: 'numeric',
});
const dateTimeFormat = new Intl.DateTimeFormat(LOCALE, {
  day: 'numeric',
  month: 'numeric',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
});

export function formatCurrency(amount: number): string {
  return currency.format(amount);
}

/** A signed amount, such as "+1,20 €" for a difference. */
export function formatSignedCurrency(amount: number): string {
  const sign = amount > 0 ? '+' : '';
  return sign + currency.format(amount);
}

/** A `YYYY-MM-DD` date, read as a calendar date (no time zone shift). */
export function formatDate(isoDate: string): string {
  const [year, month, day] = isoDate.split('-').map(Number);
  if (!year || !month || !day) return isoDate;
  return dateFormat.format(new Date(year, month - 1, day));
}

export function formatDateTime(isoTimestamp: string): string {
  return dateTimeFormat.format(new Date(isoTimestamp));
}

/** Today as `YYYY-MM-DD` in the browser's time zone. */
export function todayIsoDate(): string {
  const now = new Date();
  const pad = (value: number) => String(value).padStart(2, '0');
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
}

/**
 * Parse an amount typed by hand: a comma or a dot as the decimal separator,
 * spaces and a euro sign allowed. Returns null when it is not a number.
 */
export function parseAmount(text: string): number | null {
  const cleaned = text.replace(/[\s €]/g, '').replace(',', '.');
  if (!/^[-+]?(\d+\.?\d*|\.\d+)$/.test(cleaned)) return null;
  return Number(cleaned);
}

/** An amount as the price inputs show it: two decimals, a comma separator. */
export function amountToInput(amount: number): string {
  return amount.toFixed(2).replace('.', ',');
}

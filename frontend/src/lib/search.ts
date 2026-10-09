/**
 * Helpers for route `validateSearch`. A parameter at its default is left out,
 * so links without search parameters stay valid and URLs stay short.
 */

export function optionalPage(value: unknown): number | undefined {
  const number = typeof value === 'number' ? value : Number(value);
  return Number.isInteger(number) && number > 1 ? number : undefined;
}

export function optionalOneOf<T extends string>(
  value: unknown,
  options: readonly T[]
): T | undefined {
  return options.find((option) => option === value);
}

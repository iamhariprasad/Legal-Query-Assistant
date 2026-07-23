export function percent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function compactDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value));
}


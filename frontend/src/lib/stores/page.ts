import { writable } from 'svelte/store';

/** Título mostrado en el Header del layout (app). */
export const pageTitle = writable<string>('Bamesoft');

export function setPageTitle(value: string): void {
  pageTitle.set(value);
}

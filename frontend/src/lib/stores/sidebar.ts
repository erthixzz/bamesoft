import { writable } from 'svelte/store';

/** Estado abierto/cerrado del drawer del sidebar en móvil. */
export const sidebarOpen = writable(false);

export function openSidebar() {
  sidebarOpen.set(true);
}
export function closeSidebar() {
  sidebarOpen.set(false);
}
export function toggleSidebar() {
  sidebarOpen.update((v) => !v);
}

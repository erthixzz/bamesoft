import { writable } from 'svelte/store';
import type { ComponentType } from 'svelte';

export interface CtxItem {
  /** Texto visible. Ignorado si `divider` es true. */
  label?: string;
  /** Ícono lucide opcional. */
  icon?: ComponentType;
  /** Acción al hacer click. */
  onClick?: () => void | Promise<void>;
  /** Si se define, el ítem navega a esta ruta (tiene prioridad sobre onClick). */
  href?: string;
  /** Estilo de acción peligrosa (rojo). */
  danger?: boolean;
  /** Renderiza un separador en vez de un ítem. */
  divider?: boolean;
  /** Deshabilita el ítem. */
  disabled?: boolean;
}

export interface CtxState {
  open: boolean;
  x: number;
  y: number;
  items: CtxItem[];
}

const initial: CtxState = { open: false, x: 0, y: 0, items: [] };

export const contextMenu = writable<CtxState>(initial);

/** Abre el menú en la posición del evento (mouse o touch). */
export function openContextMenu(x: number, y: number, items: CtxItem[]): void {
  if (!items?.length) return;
  contextMenu.set({ open: true, x, y, items });
}

export function closeContextMenu(): void {
  contextMenu.update((s) => (s.open ? { ...s, open: false } : s));
}

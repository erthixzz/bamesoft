import { writable } from 'svelte/store';

export type ToastKind = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
  id: number;
  kind: ToastKind;
  message: string;
  durationMs: number;
}

const DEFAULT_DURATION_MS = 4000;

function createToasts() {
  const { subscribe, update } = writable<Toast[]>([]);
  let next = 1;

  function push(kind: ToastKind, message: string, durationMs = DEFAULT_DURATION_MS) {
    const id = next++;
    update((list) => [...list, { id, kind, message, durationMs }]);
    setTimeout(() => update((list) => list.filter((t) => t.id !== id)), durationMs);
    return id;
  }

  return {
    subscribe,
    success: (m: string, d?: number) => push('success', m, d),
    error: (m: string, d?: number) => push('error', m, d ?? 6000),
    info: (m: string, d?: number) => push('info', m, d),
    warning: (m: string, d?: number) => push('warning', m, d),
    dismiss: (id: number) => update((list) => list.filter((t) => t.id !== id)),
  };
}

export const toasts = createToasts();

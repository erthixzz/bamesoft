import { writable } from 'svelte/store';

export type ToastKind = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
  id: number;
  kind: ToastKind;
  message: string;
}

function createToasts() {
  const { subscribe, update } = writable<Toast[]>([]);
  let next = 1;

  function push(kind: ToastKind, message: string, durationMs = 4000) {
    const id = next++;
    update((list) => [...list, { id, kind, message }]);
    setTimeout(() => update((list) => list.filter((t) => t.id !== id)), durationMs);
  }

  return {
    subscribe,
    success: (m: string) => push('success', m),
    error: (m: string) => push('error', m),
    info: (m: string) => push('info', m),
    warning: (m: string) => push('warning', m),
    dismiss: (id: number) => update((list) => list.filter((t) => t.id !== id)),
  };
}

export const toasts = createToasts();

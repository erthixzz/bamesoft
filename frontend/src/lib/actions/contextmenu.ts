import { openContextMenu, type CtxItem } from '$lib/stores/contextMenu';

/**
 * Acción que abre el menú contextual del proyecto.
 * - Escritorio: click derecho.
 * - Móvil/táctil: pulsación larga (~500 ms).
 *
 * Uso: <tr use:contextmenu={items}> donde items es CtxItem[].
 */
export function contextmenu(node: HTMLElement, items: CtxItem[]) {
  let current = items;
  let pressTimer: ReturnType<typeof setTimeout> | null = null;
  let touchStart: { x: number; y: number } | null = null;

  function onContextMenu(e: MouseEvent) {
    if (!current?.length) return;
    e.preventDefault();
    openContextMenu(e.clientX, e.clientY, current);
  }

  function clearPress() {
    if (pressTimer) {
      clearTimeout(pressTimer);
      pressTimer = null;
    }
    touchStart = null;
  }

  function onTouchStart(e: TouchEvent) {
    if (!current?.length || e.touches.length !== 1) return;
    const t = e.touches[0];
    touchStart = { x: t.clientX, y: t.clientY };
    pressTimer = setTimeout(() => {
      if (touchStart) {
        // Vibración sutil si el dispositivo lo soporta.
        navigator.vibrate?.(10);
        openContextMenu(touchStart.x, touchStart.y, current);
      }
      pressTimer = null;
    }, 500);
  }

  function onTouchMove(e: TouchEvent) {
    if (!touchStart) return;
    const t = e.touches[0];
    // Si el dedo se mueve (scroll), cancela el long-press.
    if (Math.abs(t.clientX - touchStart.x) > 10 || Math.abs(t.clientY - touchStart.y) > 10) {
      clearPress();
    }
  }

  node.addEventListener('contextmenu', onContextMenu);
  node.addEventListener('touchstart', onTouchStart, { passive: true });
  node.addEventListener('touchmove', onTouchMove, { passive: true });
  node.addEventListener('touchend', clearPress);
  node.addEventListener('touchcancel', clearPress);

  return {
    update(next: CtxItem[]) {
      current = next;
    },
    destroy() {
      clearPress();
      node.removeEventListener('contextmenu', onContextMenu);
      node.removeEventListener('touchstart', onTouchStart);
      node.removeEventListener('touchmove', onTouchMove);
      node.removeEventListener('touchend', clearPress);
      node.removeEventListener('touchcancel', clearPress);
    },
  };
}

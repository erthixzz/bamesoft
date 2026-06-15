// Acción Svelte: mueve el nodo a <body> (o a un target) para que ningún
// ancestro con overflow/transform recorte o desplace popups con position:fixed.

export function portal(node: HTMLElement, target: HTMLElement | string = 'body') {
  function mount(t: HTMLElement | string) {
    const el = typeof t === 'string' ? document.querySelector<HTMLElement>(t) : t;
    if (el) el.appendChild(node);
  }
  mount(target);
  return {
    update: mount,
    destroy() {
      node.parentNode?.removeChild(node);
    },
  };
}

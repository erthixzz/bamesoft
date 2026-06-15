// Acción Svelte para tooltips estilizados (reemplaza los `title=` nativos).
// Uso: <button use:tooltip={'Salir'}> o use:tooltip={{ text, placement }}>

type Placement = 'top' | 'bottom' | 'left' | 'right';
type TooltipOptions = string | { text: string; placement?: Placement };

interface Normalized {
  text: string;
  placement: Placement;
}

function normalize(o: TooltipOptions): Normalized {
  if (typeof o === 'string') return { text: o, placement: 'top' };
  return { text: o.text, placement: o.placement ?? 'top' };
}

export function tooltip(node: HTMLElement, options: TooltipOptions) {
  let opts = normalize(options);
  let tip: HTMLDivElement | null = null;
  let arrow: HTMLDivElement | null = null;
  let showTimer: ReturnType<typeof setTimeout> | null = null;

  function place() {
    if (!tip || !arrow) return;
    const r = node.getBoundingClientRect();
    const t = tip.getBoundingClientRect();
    const gap = 8;
    let top = 0;
    let left = 0;

    if (opts.placement === 'bottom') {
      top = r.bottom + gap;
      left = r.left + r.width / 2 - t.width / 2;
    } else if (opts.placement === 'left') {
      top = r.top + r.height / 2 - t.height / 2;
      left = r.left - t.width - gap;
    } else if (opts.placement === 'right') {
      top = r.top + r.height / 2 - t.height / 2;
      left = r.right + gap;
    } else {
      top = r.top - t.height - gap;
      left = r.left + r.width / 2 - t.width / 2;
    }

    left = Math.max(6, Math.min(left, window.innerWidth - t.width - 6));
    top = Math.max(6, top);
    tip.style.top = `${top}px`;
    tip.style.left = `${left}px`;

    // Flecha
    arrow.style.left = '';
    arrow.style.top = '';
    arrow.style.bottom = '';
    arrow.style.right = '';
    if (opts.placement === 'top' || opts.placement === 'bottom') {
      const cx = r.left + r.width / 2 - left - 4;
      arrow.style.left = `${Math.max(6, Math.min(cx, t.width - 14))}px`;
      if (opts.placement === 'top') arrow.style.bottom = '-4px';
      else arrow.style.top = '-4px';
    } else {
      const cy = r.top + r.height / 2 - top - 4;
      arrow.style.top = `${Math.max(6, Math.min(cy, t.height - 14))}px`;
      if (opts.placement === 'left') arrow.style.right = '-4px';
      else arrow.style.left = '-4px';
    }
  }

  function show() {
    if (!opts.text || tip) return;
    tip = document.createElement('div');
    tip.setAttribute('role', 'tooltip');
    tip.style.cssText =
      'position:fixed;z-index:9999;pointer-events:none;background:#0f172a;color:#fff;' +
      'font-size:12px;font-weight:500;line-height:1.2;padding:6px 9px;border-radius:8px;' +
      'box-shadow:0 6px 20px rgba(15,23,42,.28);white-space:nowrap;max-width:260px;' +
      'opacity:0;transform:translateY(2px);transition:opacity .12s ease,transform .12s ease;';
    const label = document.createElement('span');
    label.textContent = opts.text;
    arrow = document.createElement('div');
    arrow.style.cssText = 'position:absolute;width:8px;height:8px;background:#0f172a;transform:rotate(45deg);';
    tip.append(label, arrow);
    document.body.appendChild(tip);
    place();
    requestAnimationFrame(() => {
      if (tip) {
        tip.style.opacity = '1';
        tip.style.transform = 'translateY(0)';
      }
    });
  }

  function hide() {
    if (showTimer) {
      clearTimeout(showTimer);
      showTimer = null;
    }
    if (tip) {
      tip.remove();
      tip = null;
      arrow = null;
    }
  }

  function enter() {
    showTimer = setTimeout(show, 120);
  }

  node.addEventListener('mouseenter', enter);
  node.addEventListener('mouseleave', hide);
  node.addEventListener('focus', show);
  node.addEventListener('blur', hide);
  node.addEventListener('click', hide);

  return {
    update(next: TooltipOptions) {
      opts = normalize(next);
      if (tip) place();
    },
    destroy() {
      hide();
      node.removeEventListener('mouseenter', enter);
      node.removeEventListener('mouseleave', hide);
      node.removeEventListener('focus', show);
      node.removeEventListener('blur', hide);
      node.removeEventListener('click', hide);
    },
  };
}

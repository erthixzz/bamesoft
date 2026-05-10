<script lang="ts">
  import {
    Wrench,
    Cog,
    HeartPulse,
    Stethoscope,
    Activity,
    Cpu,
    Atom,
    Brain,
    Microscope,
    Zap,
    Sparkles,
    CircuitBoard,
    Settings2,
    Syringe,
  } from 'lucide-svelte';

  // Mezcla de iconos: ingeniería + clínica + IA
  const ICONS = [
    Wrench, Cog, HeartPulse, Stethoscope, Activity, Cpu, Atom,
    Brain, Microscope, Zap, Sparkles, CircuitBoard, Settings2, Syringe,
  ];

  // Genera N partículas con posición / animación pseudo-aleatorias
  // pero deterministas (mismo seed → mismo render → no salta en HMR).
  function rand(seed: number) {
    const x = Math.sin(seed) * 10000;
    return x - Math.floor(x);
  }

  const particles = Array.from({ length: 22 }, (_, i) => ({
    Icon: ICONS[i % ICONS.length],
    top: rand(i * 13.7) * 100,
    left: rand(i * 31.3 + 7) * 100,
    size: 18 + Math.floor(rand(i * 5.1 + 1) * 28),
    duration: 14 + rand(i * 9.7) * 18,
    delay: rand(i * 17.3) * 12,
    opacity: 0.08 + rand(i * 4.7 + 3) * 0.18,
    rotate: Math.floor(rand(i * 3.1 + 5) * 360),
    drift: rand(i * 11.1) > 0.5 ? 'drift-a' : 'drift-b',
  }));
</script>

<div class="absolute inset-0 overflow-hidden">
  <!-- Glows de fondo -->
  <div class="absolute -left-32 -top-32 h-[480px] w-[480px] rounded-full bg-brand-300/40 blur-3xl"></div>
  <div class="absolute -bottom-32 -right-32 h-[520px] w-[520px] rounded-full bg-cyan-300/40 blur-3xl"></div>
  <div class="absolute left-1/2 top-1/2 h-[420px] w-[420px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-emerald-200/30 blur-3xl"></div>

  <!-- Cuadrícula tenue (textura "técnica") -->
  <div class="absolute inset-0 bg-[linear-gradient(to_right,rgba(15,23,42,.04)_1px,transparent_1px),linear-gradient(to_bottom,rgba(15,23,42,.04)_1px,transparent_1px)] bg-[size:48px_48px]"></div>

  <!-- Líneas conectoras estilo "neural" -->
  <svg class="absolute inset-0 h-full w-full" preserveAspectRatio="none">
    {#each [...Array(8).keys()] as i}
      {@const x1 = rand(i * 17 + 1) * 100}
      {@const y1 = rand(i * 19 + 2) * 100}
      {@const x2 = rand(i * 23 + 3) * 100}
      {@const y2 = rand(i * 29 + 4) * 100}
      <line
        x1={`${x1}%`} y1={`${y1}%`} x2={`${x2}%`} y2={`${y2}%`}
        stroke="url(#bm-line)" stroke-width="1" opacity="0.25"
      />
    {/each}
    <defs>
      <linearGradient id="bm-line" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%"   stop-color="#1971f5" stop-opacity="0.6"/>
        <stop offset="50%"  stop-color="#06b6d4" stop-opacity="0.5"/>
        <stop offset="100%" stop-color="#10b981" stop-opacity="0.3"/>
      </linearGradient>
    </defs>
  </svg>

  <!-- Partículas (iconos flotantes) -->
  {#each particles as p, i (i)}
    <div
      class={`absolute ${p.drift}`}
      style={`top:${p.top}%;left:${p.left}%;animation-duration:${p.duration}s;animation-delay:-${p.delay}s;opacity:${p.opacity}`}
    >
      <svelte:component
        this={p.Icon}
        size={p.size}
        style={`transform:rotate(${p.rotate}deg)`}
        class="text-brand-700"
      />
    </div>
  {/each}
</div>

<style>
  /* Dos animaciones diferentes para variar el movimiento */
  @keyframes drift-a {
    0%   { transform: translate(0, 0) rotate(0deg); }
    50%  { transform: translate(20px, -30px) rotate(8deg); }
    100% { transform: translate(0, 0) rotate(0deg); }
  }
  @keyframes drift-b {
    0%   { transform: translate(0, 0) rotate(0deg); }
    50%  { transform: translate(-25px, 25px) rotate(-10deg); }
    100% { transform: translate(0, 0) rotate(0deg); }
  }
  :global(.drift-a) { animation: drift-a linear infinite; }
  :global(.drift-b) { animation: drift-b linear infinite; }
</style>

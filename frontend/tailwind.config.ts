import type { Config } from 'tailwindcss';

export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        // Paleta Bamesoft (clínico, sobrio)
        brand: {
          50: '#eef7ff',
          100: '#d9edff',
          200: '#bce0ff',
          300: '#8ecdff',
          400: '#58afff',
          500: '#2f8eff',
          600: '#1971f5',
          700: '#155ce0',
          800: '#174cb4',
          900: '#19438d',
        },
        accent: {
          500: '#10b981',
          600: '#059669',
        },
        // Escala completa: la UI ya usaba `danger-50/100/700/800` (badges,
        // errores, satisfacción baja) y sin estos tonos Tailwind no generaba
        // esas clases y el color simplemente no salía.
        danger: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config;

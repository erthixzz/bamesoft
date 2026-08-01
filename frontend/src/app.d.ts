// See https://kit.svelte.dev/docs/types#app
import type { Session, User } from '@supabase/supabase-js';

/** Opciones de `turnstile.render()` que realmente usamos. */
interface TurnstileOptions {
  sitekey: string;
  callback?: (token: string) => void;
  'expired-callback'?: () => void;
  'error-callback'?: () => void;
  theme?: 'light' | 'dark' | 'auto';
  size?: 'normal' | 'compact' | 'flexible';
  language?: string;
}

declare global {
  namespace App {
    interface Locals {
      session: Session | null;
      user: User | null;
    }
    interface PageData {
      session: Session | null;
    }
  }

  /** Lo inyecta el script de Cloudflare Turnstile (ver `Turnstile.svelte`). */
  interface Window {
    turnstile?: {
      render: (el: HTMLElement | string, opts: TurnstileOptions) => string;
      reset: (widgetId?: string) => void;
      remove: (widgetId?: string) => void;
    };
  }
}

export {};

import { env } from '$env/dynamic/public';
import { supabase } from '$lib/supabase';

const BASE_URL = env.PUBLIC_API_URL ?? 'http://localhost:8000/api/v1';

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public detail?: unknown,
  ) {
    super(message);
  }
}

type QueryParams = Record<string, unknown>;

interface RequestOpts extends Omit<RequestInit, 'body' | 'headers'> {
  body?: unknown;
  headers?: Record<string, string>;
  query?: QueryParams;
  isFormData?: boolean;
}

function buildUrl(path: string, query?: QueryParams): string {
  const url = new URL(path.startsWith('http') ? path : `${BASE_URL}${path}`);
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v === undefined || v === null) continue;
      url.searchParams.set(k, String(v));
    }
  }
  return url.toString();
}

async function authHeader(): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function request<T = unknown>(path: string, opts: RequestOpts = {}): Promise<T> {
  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...(await authHeader()),
    ...(opts.headers ?? {}),
  };

  let body: BodyInit | undefined;
  if (opts.isFormData) {
    body = opts.body as FormData;
  } else if (opts.body !== undefined) {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(opts.body);
  }

  const url = buildUrl(path, opts.query);
  const { query: _q, isFormData: _fd, headers: _hIn, body: _bIn, ...fetchOpts } = opts;
  const init: RequestInit = { ...fetchOpts, headers, body };

  let res: Response;
  try {
    res = await fetch(url, init);
  } catch {
    // Render cold start / red: primer intento a veces falla sin respuesta CORS
    await new Promise((r) => setTimeout(r, 2000));
    res = await fetch(url, init);
  }

  if (!res.ok) {
    let detail: unknown = await res.text();
    try {
      detail = JSON.parse(detail as string);
    } catch {
      /* texto plano */
    }
    const detailStr =
      typeof detail === 'object' && detail && 'detail' in detail
        ? String((detail as { detail: unknown }).detail)
        : typeof detail === 'string'
          ? detail
          : '';
    const msg = detailStr
      ? `${res.status} ${res.statusText} — ${detailStr}`
      : `${res.status} ${res.statusText}`;
    throw new ApiError(res.status, msg, detail);
  }

  if (res.status === 204) return undefined as T;
  const contentType = res.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) return (await res.json()) as T;
  return (await res.text()) as unknown as T;
}

export const api = {
  get: <T>(path: string, query?: object) =>
    request<T>(path, { method: 'GET', query: query as QueryParams | undefined }),
  post: <T>(path: string, body?: unknown) => request<T>(path, { method: 'POST', body }),
  patch: <T>(path: string, body?: unknown) => request<T>(path, { method: 'PATCH', body }),
  put: <T>(path: string, body?: unknown) => request<T>(path, { method: 'PUT', body }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
  upload: <T>(path: string, form: FormData) =>
    request<T>(path, { method: 'POST', body: form, isFormData: true }),
};

"use client";

import camelcaseKeys from "camelcase-keys";
import snakecaseKeys from "snakecase-keys";
import { getToken, setToken, clearToken } from "./token-store";

// ---------------------------------------------------------------------------
// Error type
// ---------------------------------------------------------------------------

export class ApiError extends Error {
  constructor(
    public readonly detail: string,
    public readonly code: string,
    public readonly status: number,
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/** Prevent concurrent refresh requests (race guard). */
let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  try {
    const res = await fetch("/api/auth/refresh", {
      method: "POST",
      headers: { "content-type": "application/json" },
      credentials: "include",
      body: JSON.stringify({}),
    });

    if (!res.ok) {
      // Refresh token is dead — clear everything so auth-context can redirect to login.
      clearToken();
      return null;
    }

    const data = await res.json();
    // Backend returns { access_token, expires_in }
    const newToken = (data as { access_token: string }).access_token;
    setToken(newToken);
    return newToken;
  } catch {
    clearToken();
    return null;
  }
}

function getRefreshPromise(): Promise<string | null> {
  if (!refreshPromise) {
    refreshPromise = refreshAccessToken().finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

// ---------------------------------------------------------------------------
// Public API fetch
// ---------------------------------------------------------------------------

/**
 * Typed fetch wrapper that:
 *  - Attaches the in-memory Bearer access token
 *  - Sends credentials (cookies) for refresh-token transport
 *  - Auto-refreshes on 401 and retries once
 *  - Converts request bodies to snake_case and responses to camelCase
 *  - Normalises backend errors into ApiError({ detail, code, status })
 */
export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const { body, headers: rawHeaders, ...rest } = options;

  // Build headers
  const headers: Record<string, string> = {
    ...(rawHeaders as Record<string, string> | undefined),
  };

  let jsonBody: string | null = null;
  if (body) {
    // Convert outgoing JSON to snake_case
    const parsed = JSON.parse(body as string);
    const snakeBody = snakecaseKeys(parsed, { deep: true });
    jsonBody = JSON.stringify(snakeBody);
    headers["content-type"] = "application/json";
  }

  // Attach Bearer token if available
  const token = getToken();
  if (token) {
    headers["authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(path, {
    ...rest,
    headers,
    credentials: "include",
    body: jsonBody,
  });

  // ----- Error handling -----
  if (!res.ok) {
    // Try to parse { detail, code } from the response
    let detail = `Request failed (${res.status})`;
    let code = "unknown_error";
    try {
      const errData = await res.json();
      if (typeof errData.detail === "string") detail = errData.detail;
      if (typeof errData.code === "string") code = errData.code;
    } catch {
      // body isn't JSON — use defaults
    }

    // Auto-refresh on 401 with invalid_access_token (expired access token)
    if (res.status === 401 && code === "invalid_access_token") {
      const newToken = await getRefreshPromise();
      if (newToken) {
        // Retry the original request with the fresh token
        headers["authorization"] = `Bearer ${newToken}`;
        const retryRes = await fetch(path, {
          ...rest,
          headers,
          credentials: "include",
          body: jsonBody,
        });
        if (retryRes.ok) {
          const raw = await retryRes.json();
          return camelcaseKeys(raw, { deep: true }) as T;
        }
        // If retry also fails, fall through to throw below
        if (retryRes.status !== 401) {
          try {
            const retryErr = await retryRes.json();
            detail = typeof retryErr.detail === "string" ? retryErr.detail : detail;
            code = typeof retryErr.code === "string" ? retryErr.code : code;
          } catch { /* ignore */ }
        }
      }
    }

    throw new ApiError(detail, code, res.status);
  }

  // ----- Success -----
  // 204 No Content (e.g. logout)
  if (res.status === 204) {
    return undefined as T;
  }

  const raw = await res.json();
  // Convert snake_case response → camelCase for frontend consumption
  return camelcaseKeys(raw, { deep: true }) as T;
}

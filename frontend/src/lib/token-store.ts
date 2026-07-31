/**
 * In-memory store for the short-lived access token.
 * Never persisted to localStorage — the refresh cookie (httpOnly, samesite=lax)
 * survives page reloads and silently re-issues a new access token.
 */

let accessToken: string | null = null;

export function getToken(): string | null {
  return accessToken;
}

export function setToken(token: string): void {
  accessToken = token;
}

export function clearToken(): void {
  accessToken = null;
}

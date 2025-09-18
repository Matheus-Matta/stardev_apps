// util simples para validar expiração do JWT sem depender do backend
export function parseJwt(token) {
  try {
    const [, payload] = token.split(".");
    return JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
  } catch {
    return null;
  }
}

export function isJwtExpired(token, skewSeconds = 10) {
  const p = parseJwt(token);
  if (!p || !p.exp) return true;
  const now = Math.floor(Date.now() / 1000);
  return p.exp <= (now + skewSeconds);
}

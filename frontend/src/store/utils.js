export function unwrapData(resp) {
  const root = resp?.data ?? resp;
  const data = root?.data ?? root;
  const { ok, detail, ...rest } = data || {};
  return data && data !== root ? data : rest;
}
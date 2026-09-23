// V5 instance id helper with WebView-safe fallback.
export function createInstanceId(prefix="id") {
  const uuid=globalThis.crypto?.randomUUID?.();
  if (uuid) return uuid;
  return prefix+"_"+Date.now().toString(36)+"_"+Math.random().toString(36).slice(2)+Math.random().toString(36).slice(2);
}

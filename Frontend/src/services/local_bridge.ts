const COMPANION_ENDPOINTS = [
  "http://127.0.0.1:8001/execute",
  "http://localhost:8001/execute"
];

export async function sendActionToLocalCompanion(action: string, target: string = ""): Promise<boolean> {
  for (const endpoint of COMPANION_ENDPOINTS) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, target }),
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (res.ok) {
        console.log(`[LocalBridge] Successfully executed action '${action}' via ${endpoint}.`);
        return true;
      }
    } catch (err) {
      console.warn(`[LocalBridge] Failed request to ${endpoint}:`, err);
    }
  }
  return false;
}

export async function parseAndExecuteActionDirective(text: string): Promise<string> {
  if (!text) return text;

  const actionRegex = /\[ACTION:([A-Z_]+)(?::([^\]]+))?\]/g;
  let match;
  let companionOffline = false;

  while ((match = actionRegex.exec(text)) !== null) {
    const action = match[1];
    const target = match[2] || "";

    if (action === "OPEN_URL" && target && typeof window !== "undefined") {
      try {
        window.open(target, "_blank");
      } catch (e) {
        console.warn("[LocalBridge] Window open error:", e);
      }
    }

    const success = await sendActionToLocalCompanion(action, target);
    if (!success && action !== "OPEN_URL") {
      companionOffline = true;
    }
  }

  let cleaned = text.replace(/\[ACTION:[^\]]+\]\s*/g, "").trim();

  if (companionOffline) {
    const isHttps = typeof window !== "undefined" && window.location.protocol === "https:";
    if (isHttps) {
      cleaned += "\n\n*(Note: Your browser is blocking HTTP calls from an HTTPS site [Mixed Content]. Allow insecure content in site settings or run `python local_companion.py` locally.)*";
    } else {
      cleaned += "\n\n*(Note: Local Companion Agent on http://127.0.0.1:8001 is offline. Run `python local_companion.py` on your PC to enable local OS actions.)*";
    }
  }

  return cleaned;
}

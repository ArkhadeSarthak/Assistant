const LOCAL_COMPANION_URL = "http://127.0.0.1:8001/execute";

export async function sendActionToLocalCompanion(action: string, target: string = ""): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);

    const res = await fetch(LOCAL_COMPANION_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, target }),
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (res.ok) {
      console.log(`[LocalBridge] Successfully sent action '${action}' to Local Companion Agent on http://127.0.0.1:8001.`);
      return true;
    }
  } catch (err) {
    console.warn(`[LocalBridge] Local Companion Agent (http://127.0.0.1:8001) unavailable:`, err);
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
    cleaned += "\n\n*(Note: Local Companion Agent on http://127.0.0.1:8001 is offline. Run `python local_companion.py` on your PC to enable local OS actions.)*";
  }

  return cleaned;
}

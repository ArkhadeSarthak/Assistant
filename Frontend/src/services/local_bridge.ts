const LOCAL_COMPANION_URL = "http://127.0.0.1:8001/execute";

export async function sendActionToLocalCompanion(action: string, target: string = ""): Promise<boolean> {
  try {
    const res = await fetch(LOCAL_COMPANION_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, target }),
    });
    if (res.ok) {
      console.log(`[LocalBridge] Successfully sent action '${action}' to Local Companion Agent.`);
      return true;
    }
  } catch (err) {
    console.warn(`[LocalBridge] Local Companion Agent (http://127.0.0.1:8001) unavailable:`, err);
  }
  return false;
}

export function parseAndExecuteActionDirective(text: string): string {
  if (!text) return text;

  const actionRegex = /\[ACTION:([A-Z_]+)(?::([^\]]+))?\]/g;
  let match;

  while ((match = actionRegex.exec(text)) !== null) {
    const action = match[1];
    const target = match[2] || "";
    sendActionToLocalCompanion(action, target);
  }

  // Clean raw action tags from user message display
  return text.replace(/\[ACTION:[^\]]+\]\s*/g, "");
}

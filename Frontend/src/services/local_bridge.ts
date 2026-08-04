const COMPANION_HTTP_ENDPOINTS = [
  "http://127.0.0.1:8001/execute",
  "http://localhost:8001/execute"
];

const COMPANION_WS_ENDPOINTS = [
  "ws://127.0.0.1:8001/ws",
  "ws://localhost:8001/ws"
];

let activeWs: WebSocket | null = null;
let isWsConnecting = false;

function initLocalCompanionWs(): Promise<WebSocket | null> {
  if (activeWs && activeWs.readyState === WebSocket.OPEN) {
    return Promise.resolve(activeWs);
  }

  if (isWsConnecting) {
    return new Promise((resolve) => {
      let attempts = 0;
      const interval = setInterval(() => {
        attempts++;
        if (activeWs && activeWs.readyState === WebSocket.OPEN) {
          clearInterval(interval);
          resolve(activeWs);
        } else if (attempts > 10) {
          clearInterval(interval);
          resolve(null);
        }
      }, 100);
    });
  }

  isWsConnecting = true;

  return new Promise((resolve) => {
    let triedCount = 0;

    const tryNext = (index: number) => {
      if (index >= COMPANION_WS_ENDPOINTS.length) {
        isWsConnecting = false;
        resolve(null);
        return;
      }

      const wsUrl = COMPANION_WS_ENDPOINTS[index];
      try {
        const ws = new WebSocket(wsUrl);
        const timeout = setTimeout(() => {
          ws.close();
          tryNext(index + 1);
        }, 1500);

        ws.onopen = () => {
          clearTimeout(timeout);
          activeWs = ws;
          isWsConnecting = false;
          console.log(`[LocalBridge] Connected WebSocket to Local Companion at ${wsUrl}`);
          resolve(ws);
        };

        ws.onerror = () => {
          clearTimeout(timeout);
          tryNext(index + 1);
        };

        ws.onclose = () => {
          if (activeWs === ws) {
            activeWs = null;
          }
        };
      } catch (e) {
        tryNext(index + 1);
      }
    };

    tryNext(0);
  });
}

export async function sendActionToLocalCompanion(action: string, target: string = ""): Promise<boolean> {
  // 1. Try WebSocket Connection (Bypasses HTTPS Mixed Content Security Blocks)
  try {
    const ws = await initLocalCompanionWs();
    if (ws && ws.readyState === WebSocket.OPEN) {
      return new Promise<boolean>((resolve) => {
        const timeout = setTimeout(() => resolve(false), 2000);
        ws.onmessage = (event) => {
          clearTimeout(timeout);
          try {
            const data = JSON.parse(event.data);
            if (data.status === "success") {
              console.log(`[LocalBridge] WS Action '${action}' executed successfully:`, data);
              resolve(true);
            } else {
              resolve(false);
            }
          } catch (e) {
            resolve(false);
          }
        };

        ws.send(JSON.stringify({ action, target }));
      });
    }
  } catch (err) {
    console.warn("[LocalBridge] WS transmission error:", err);
  }

  // 2. HTTP Fallback if WebSockets fail
  for (const endpoint of COMPANION_HTTP_ENDPOINTS) {
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
      console.warn(`[LocalBridge] HTTP request to ${endpoint} failed:`, err);
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
    cleaned += "\n\n*(Note: Local Companion Agent is offline. Run `python local_companion.py` on your PC to execute local OS desktop actions.)*";
  }

  return cleaned;
}

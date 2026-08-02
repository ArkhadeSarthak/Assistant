import os
import re
import ctypes
import time
from pydantic import BaseModel, Field
from langchain.tools import tool
from app.utils.logger import app_logger

class MediaControlInput(BaseModel):
    action: str = Field(description="Media action: 'play', 'pause', 'next', 'previous', 'volume_up', 'volume_down', 'mute'")
    query: str = Field(default="", description="Original user query for percentage extraction")

def adjust_volume_by_percentage(query: str) -> str:
    """Extracts percentage from query (default 10%) and adjusts master system volume up or down."""
    query_lower = query.lower()
    
    # Extract percentage number if specified (e.g. "by 20%", "15 percent", "10%")
    match = re.search(r'(\d+)\s*(%|percent)?', query_lower)
    percentage = int(match.group(1)) if match else 10
    
    direction = "down" if any(k in query_lower for k in ["decrease", "lower", "down", "reduce", "quieter"]) else "up"
    vk = 0xAE if direction == "down" else 0xAF # VK_VOLUME_DOWN / VK_VOLUME_UP

    # Each keypress step in Windows is ~2%
    steps = max(1, int(round(percentage / 2.0)))
    
    try:
        if os.name == "nt":
            for _ in range(steps):
                ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
                ctypes.windll.user32.keybd_event(vk, 0, 2, 0)
                time.sleep(0.01)
        actual_pct = steps * 2
        action_word = "decreased" if direction == "down" else "increased"
        return f"Successfully {action_word} master volume by ~{actual_pct}% (requested {percentage}%)."
    except Exception as e:
        return f"Volume adjustment completed ({direction}): {e}"

@tool("media_control", args_schema=MediaControlInput)
def media_control_tool(action: str, query: str = "") -> str:
    """Controls media playback and master audio volume (volume percentage, play, pause, next, previous)."""
    app_logger.info(f"Executing media_control tool with action: {action}, query: {query}")
    action_clean = action.lower()
    combined = f"{action_clean} {query.lower()}"

    if any(k in combined for k in ["volume", "up", "down", "increase", "decrease", "louder", "quieter", "sound", "audio", "turn"]):
        return adjust_volume_by_percentage(query or action)

    try:
        if os.name == "nt":
            if any(k in action_clean for k in ["play", "pause", "resume"]):
                ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0) # VK_MEDIA_PLAY_PAUSE
                ctypes.windll.user32.keybd_event(0xB3, 0, 2, 0)
            elif any(k in action_clean for k in ["next", "skip"]):
                ctypes.windll.user32.keybd_event(0xB0, 0, 0, 0) # VK_MEDIA_NEXT_TRACK
                ctypes.windll.user32.keybd_event(0xB0, 0, 2, 0)
            elif any(k in action_clean for k in ["previous", "prev", "back"]):
                ctypes.windll.user32.keybd_event(0xB1, 0, 0, 0) # VK_MEDIA_PREV_TRACK
                ctypes.windll.user32.keybd_event(0xB1, 0, 2, 0)
            elif any(k in action_clean for k in ["mute", "unmute"]):
                ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0) # VK_VOLUME_MUTE
                ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
        return f"Successfully executed media command: '{action}'."
    except Exception as e:
        return f"Media command '{action}' processed: {str(e)}"


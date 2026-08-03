import os
import ctypes
import psutil
from datetime import datetime
from pydantic import BaseModel, Field
from langchain.tools import tool
from app.utils.logger import app_logger

class SystemStatsInput(BaseModel):
    dummy: str = Field(default="", description="Empty argument for system metrics query")

@tool("get_system_stats", args_schema=SystemStatsInput)
def get_system_stats_tool(dummy: str = "") -> str:
    """Returns CPU, RAM, Disk usage, and Battery status."""
    app_logger.info("Gathering system health metrics")
    cpu_usage = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    battery = psutil.sensors_battery()
    battery_info = f"{round(battery.percent)}% ({'Plugged in' if battery.power_plugged else 'Discharging'})" if battery else "N/A"

    return f"""### 📊 System Health Metrics

- **CPU Usage**: `{cpu_usage}%`
- **RAM Usage**: `{ram.percent}%` ({round(ram.used/(1024**3), 1)}GB / {round(ram.total/(1024**3), 1)}GB)
- **Disk Usage**: `{disk.percent}%` ({round(disk.used/(1024**3), 1)}GB / {round(disk.total/(1024**3), 1)}GB)
- **Battery Status**: `{battery_info}`
"""

class ScreenshotInput(BaseModel):
    filename: str = Field(default="screenshot.png", description="Filename for saved screenshot")

def is_cloud_environment() -> bool:
    return os.name != "nt" or bool(os.environ.get("RENDER")) or bool(os.environ.get("VERCEL"))

@tool("take_screenshot", args_schema=ScreenshotInput)
def take_screenshot_tool(filename: str = "screenshot.png") -> str:
    """Captures a screenshot of the local computer screen and saves it."""
    app_logger.info(f"Taking screen capture to file: {filename}")
    if is_cloud_environment():
        return "ℹ️ **Cloud Environment Notice**: Capturing your computer's screen requires running the AURA AI backend locally on your machine (`http://localhost:8000`). Cloud servers on Render do not have access to your local display."
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        os.makedirs("./storage", exist_ok=True)
        save_path = os.path.join("./storage", filename)
        img.save(save_path)
        return f"Screenshot successfully saved to '{save_path}' at {datetime.now().strftime('%H:%M:%S')}."
    except Exception as e:
        app_logger.error(f"Screenshot error: {e}")
        return f"Unable to capture screen: {str(e)}"

class LockComputerInput(BaseModel):
    dummy: str = Field(default="", description="Empty argument for lock computer")

@tool("lock_computer", args_schema=LockComputerInput)
def lock_computer_tool(dummy: str = "") -> str:
    """Locks the computer workstation screen."""
    app_logger.info("Executing lock_computer_tool")
    if is_cloud_environment():
        return "🔒 [ACTION:LOCK_SCREEN] Workstation screen locked successfully."
    try:
        if os.name == "nt":
            res = ctypes.windll.user32.LockWorkStation()
            if res == 0:
                os.system("rundll32.exe user32.dll,LockWorkStation")
        return "🔒 Workstation screen locked successfully."
    except Exception as e:
        app_logger.error(f"Lock workstation error: {e}")
        return f"Error locking workstation: {str(e)}"

class SleepComputerInput(BaseModel):
    dummy: str = Field(default="", description="Empty argument for sleep computer")

@tool("sleep_computer", args_schema=SleepComputerInput)
def sleep_computer_tool(dummy: str = "") -> str:
    """Puts the local computer into sleep/standby mode."""
    app_logger.info("Executing sleep_computer_tool")
    if is_cloud_environment():
        return "💤 [ACTION:SLEEP] Computer entering low-power sleep mode."
    try:
        if os.name == "nt":
            os.system("powershell -c \"Add-Type -Assembly System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)\"")
        return "💤 **Sleep Mode Initiated**: Computer entering low-power sleep mode."
    except Exception as e:
        return f"Error initiating sleep mode: {str(e)}"

class ShutdownComputerInput(BaseModel):
    dummy: str = Field(default="", description="Empty argument for shutdown computer")

@tool("shutdown_computer", args_schema=ShutdownComputerInput)
def shutdown_computer_tool(dummy: str = "") -> str:
    """Initiates system shutdown."""
    app_logger.info("Executing shutdown_computer_tool")
    if is_cloud_environment():
        return "🔌 [ACTION:SHUTDOWN] System shutdown initiated in 10 seconds."
    try:
        if os.name == "nt":
            os.system("shutdown /s /t 10")
        return "🔌 **System Shutdown Initiated**: Shutting down computer in 10 seconds. (Run `shutdown /a` to cancel)."
    except Exception as e:
        return f"Error initiating shutdown: {str(e)}"

class RestartComputerInput(BaseModel):
    dummy: str = Field(default="", description="Empty argument for restart computer")

@tool("restart_computer", args_schema=RestartComputerInput)
def restart_computer_tool(dummy: str = "") -> str:
    """Initiates system restart."""
    app_logger.info("Executing restart_computer_tool")
    if is_cloud_environment():
        return "🔄 [ACTION:RESTART] System restart initiated in 10 seconds."
    try:
        if os.name == "nt":
            os.system("shutdown /r /t 10")
        return "🔄 **System Restart Initiated**: Restarting computer in 10 seconds. (Run `shutdown /a` to cancel)."
    except Exception as e:
        return f"Error initiating restart: {str(e)}"

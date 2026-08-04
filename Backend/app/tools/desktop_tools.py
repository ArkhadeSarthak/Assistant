import os
import subprocess
import psutil
import time
import shutil
import webbrowser
from typing import Optional, Dict
from pydantic import BaseModel, Field
from langchain.tools import tool
from app.utils.logger import app_logger

class LaunchAppInput(BaseModel):
    app_name: str = Field(description="Natural language name of application to launch (e.g. 'VS Code', 'Spotify', 'Calculator', 'Chrome', 'Notepad', 'YouTube', 'LinkedIn')")

APP_MAP = {
    "vscode": "code",
    "vs code": "code",
    "visual studio code": "code",
    "calculator": "calc",
    "calc": "calc",
    "notepad": "notepad",
    "chrome": "chrome",
    "spotify": "spotify",
    "cmd": "cmd",
    "terminal": "cmd",
    "powershell": "powershell",
    "explorer": "explorer",
    "camera": "microsoft.windows.camera:",
    "photos": "ms-photos:",
    "settings": "ms-settings:",
    "clock": "ms-clock:",
    "paint": "mspaint",
    "linkedin": "linkedin:",
    "whatsapp": "whatsapp:",
    "slack": "slack:",
    "teams": "teams:",
    "discord": "discord:",
}

WEB_URL_MAP = {
    "youtube": "https://www.youtube.com",
    "linkedin": "https://www.linkedin.com",
    "whatsapp": "https://web.whatsapp.com",
    "slack": "https://app.slack.com",
    "teams": "https://teams.microsoft.com",
    "discord": "https://discord.com",
    "spotify": "https://open.spotify.com",
    "github": "https://github.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "reddit": "https://www.reddit.com",
    "chatgpt": "https://chatgpt.com",
}

START_MENU_CACHE: Dict[str, str] = {}
_cache_built = False

def build_start_menu_cache():
    """Indexes Windows Start Menu shortcuts into memory once for sub-millisecond instant app lookups."""
    global _cache_built, START_MENU_CACHE
    if _cache_built:
        return
    if os.name != "nt":
        _cache_built = True
        return

    start_dirs = [
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Chrome Apps"),
        os.path.expandvars(r"%USERPROFILE%\Desktop"),
        r"C:\Users\Public\Desktop",
    ]

    for d in start_dirs:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith(".lnk"):
                    clean_name = file[:-4].lower().strip()
                    full_path = os.path.join(root, file)
                    if clean_name not in START_MENU_CACHE:
                        START_MENU_CACHE[clean_name] = full_path

    _cache_built = True

try:
    import threading
    threading.Thread(target=build_start_menu_cache, daemon=True).start()
except Exception:
    pass

def find_start_menu_shortcut(app_name: str) -> Optional[str]:

    """Sub-millisecond lookup of application shortcut (.lnk) from in-memory cache."""
    build_start_menu_cache()
    if os.name != "nt":
        return None
        
    app_clean = app_name.lower().strip()
    
    # Check exact match in cache
    if app_clean in START_MENU_CACHE:
        return START_MENU_CACHE[app_clean]

    alias_map = {
        "vscode": ["visual studio code", "vscode", "code"],
        "vs code": ["visual studio code", "vscode"],
        "code": ["visual studio code", "code"],
        "chrome": ["google chrome", "chrome"],
        "google chrome": ["google chrome", "chrome"],
        "edge": ["microsoft edge", "edge"],
        "notepad": ["notepad"],
        "paint": ["paint", "mspaint"],
        "spotify": ["spotify"],
        "whatsapp": ["whatsapp"],
        "linkedin": ["linkedin"],
        "youtube": ["youtube"],
        "github": ["github", "github desktop"],
        "chatgpt": ["chatgpt"],
        "twitter": ["twitter", "x"],
        "camera": ["camera"],
    }
    
    target_names = alias_map.get(app_clean, [app_clean])
    for t in target_names:
        if t in START_MENU_CACHE:
            return START_MENU_CACHE[t]
        for key, path in START_MENU_CACHE.items():
            if t == key or t in key.split():
                return path

    return None

def find_local_app_executable(command: str) -> Optional[str]:
    """Fast single-pass check for local app executable, protocol, or shortcut."""
    if not command:
        return None

    clean_cmd = command[:-1] if command.endswith(":") else command

    # 1. Check Start Menu shortcut cache
    shortcut = find_start_menu_shortcut(clean_cmd)
    if shortcut:
        return shortcut

    # 2. Check system PATH via shutil.which
    which_path = shutil.which(clean_cmd) or shutil.which(f"{clean_cmd}.exe")
    if which_path:
        return which_path

    # 3. Check Windows Registry App Paths
    if os.name == "nt":
        try:
            import winreg
            key_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{clean_cmd}.exe"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as k:
                val, _ = winreg.QueryValueEx(k, "")
                if val and os.path.exists(val):
                    return val
        except Exception:
            pass

    # 4. Check Windows HKCR Protocol Handlers (e.g. microsoft.windows.camera:, ms-settings:, etc.)
    if os.name == "nt":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, clean_cmd):
                return command
        except Exception:
            pass

    # 5. Check common installation directories
    if os.name == "nt":
        user_profile = os.environ.get("USERPROFILE", "")
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        
        search_paths = [
            os.path.join(program_files, clean_cmd, f"{clean_cmd}.exe"),
            os.path.join(program_files_x86, clean_cmd, f"{clean_cmd}.exe"),
            os.path.join(local_app_data, "Programs", clean_cmd, f"{clean_cmd}.exe"),
            os.path.join(user_profile, "AppData", "Local", "Microsoft", "WindowsApps", f"{clean_cmd}.exe"),
        ]
        if clean_cmd.lower() == "spotify":
            search_paths.append(os.path.join(local_app_data, "Spotify", "Spotify.exe"))
        elif clean_cmd.lower() in ["code", "vscode"]:
            search_paths.append(os.path.join(local_app_data, "Programs", "Microsoft VS Code", "Code.exe"))

        for p in search_paths:
            if os.path.exists(p):
                return p

    return None

def launch_in_chrome(url: str, app_mode: bool = True):
    """Launches a URL in Google Chrome using the Default user profile."""
    chrome_path = (
        shutil.which("chrome")
        or shutil.which("google-chrome")
        or r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        or r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    )
    
    if os.name == "nt" and os.path.exists(chrome_path):
        args = [chrome_path, "--profile-directory=Default"]
        if app_mode:
            args.append(f"--app={url}")
        else:
            args.append(url)
        subprocess.Popen(args)
    else:
        webbrowser.open(url)

def is_cloud_environment() -> bool:
    return os.name != "nt" or bool(os.environ.get("RENDER")) or bool(os.environ.get("VERCEL"))

@tool("launch_app", args_schema=LaunchAppInput)
def launch_app_tool(app_name: str) -> str:
    """Instantly launches an installed desktop application or web platform."""
    t_start = time.time()
    app_logger.info(f"Executing launch_app tool for: {app_name}")
    name_clean = app_name.lower().strip()
    command = APP_MAP.get(name_clean, name_clean)
    display_name = app_name.capitalize() if app_name else "Application"

    # Fast single-pass check for local app executable / shortcut
    local_target = find_local_app_executable(command) or find_local_app_executable(name_clean)

    if local_target:
        if is_cloud_environment():
            url = WEB_URL_MAP.get(name_clean) or f"https://www.{name_clean}.com"
            return f"🚀 [ACTION:LAUNCH_APP:{command}] [ACTION:OPEN_URL:{url}] Launched local application: '{display_name}'."
        try:
            if local_target.endswith(".lnk"):
                os.startfile(local_target)
            elif os.name == "nt":
                if os.path.exists(local_target):
                    os.startfile(local_target)
                else:
                    subprocess.Popen(f'start "" "{local_target}"', shell=True)
            else:
                subprocess.Popen([local_target])
            
            app_logger.info(f"Launched local app '{display_name}' in {round((time.time() - t_start)*1000, 2)}ms")
            return f"🚀 Successfully launched local application: **{display_name}**."
        except Exception as e:
            app_logger.warning(f"Failed to launch local application '{app_name}': {e}")

    # Fallback to Web URL in Chrome / Default Web Browser if local app is not installed
    url = WEB_URL_MAP.get(name_clean) or f"https://www.{name_clean}.com"
    if not is_cloud_environment():
        try:
            launch_in_chrome(url, app_mode=True)
        except Exception as e:
            app_logger.warning(f"Failed to launch Chrome URL for '{app_name}': {e}")
            webbrowser.open(url)

    app_logger.info(f"Opened web URL for '{display_name}' in {round((time.time() - t_start)*1000, 2)}ms")
    return f"🌐 Local app **{display_name}** not found on device. Opened web version in Chrome: [{url}]({url})"

class ListRunningAppsInput(BaseModel):
    limit: int = Field(default=10, description="Number of top processes to list")

@tool("list_running_apps", args_schema=ListRunningAppsInput)
def list_running_apps_tool(limit: int = 10) -> str:
    """Lists currently running desktop applications and active processes."""
    app_logger.info("Listing running desktop applications")
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            info = proc.info
            if info['name'] and not info['name'].startswith('System'):
                processes.append(f"PID: {info['pid']} | Name: {info['name']} | Memory: {round(info['memory_info'].rss / (1024*1024), 1)}MB")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        if len(processes) >= limit:
            break
    return "\n".join(processes) if processes else "No active user processes found."

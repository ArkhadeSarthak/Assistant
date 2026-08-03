import os
import subprocess
import psutil
import time
import shutil
import webbrowser
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

def find_start_menu_shortcut(app_name: str) -> str:
    """Scans Windows Start Menu directories for a matching application shortcut (.lnk)."""
    if os.name != "nt":
        return None
        
    app_clean = app_name.lower().strip()
    target_names = [app_clean]
    
    # Map common aliases to expected Start Menu shortcut names
    alias_map = {
        "vscode": ["visual studio code", "vscode", "code"],
        "vs code": ["visual studio code", "vscode"],
        "code": ["visual studio code", "code"],
        "chrome": ["google chrome", "chrome"],
        "google chrome": ["google chrome", "chrome"],
        "edge": ["microsoft edge", "edge"],
        "notepad": ["notepad"],
        "paint": ["paint", "mspaint"],
        "postman": ["postman"],
        "spotify": ["spotify"],
        "whatsapp": ["whatsapp"],
        "camera": ["camera"],
        "power bi": ["power bi desktop", "power bi"],
        "android studio": ["android studio"],
        "mysql workbench": ["mysql workbench"],
        "word": ["word", "microsoft word"],
        "excel": ["excel", "microsoft excel"],
        "powerpoint": ["powerpoint", "microsoft powerpoint"]
    }
    
    if app_clean in alias_map:
        target_names = alias_map[app_clean]

    start_dirs = [
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
    ]
    
    for d in start_dirs:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith(".lnk"):
                    name_lower = file[:-4].lower()
                    for t in target_names:
                        if t == name_lower or t in name_lower.split():
                            return os.path.join(root, file)
    return None

def check_local_app_availability(command: str) -> bool:
    """Checks if a command, binary, Start Menu shortcut, protocol scheme, or app executable exists locally on disk or PATH."""
    if not command:
        return False
    
    clean_cmd = command[:-1] if command.endswith(":") else command

    # 1. Check Start Menu shortcuts
    if find_start_menu_shortcut(clean_cmd):
        return True

    # 2. Check system PATH via shutil.which
    if shutil.which(clean_cmd) or shutil.which(f"{clean_cmd}.exe"):
        return True

    # 3. Check Windows Registry App Paths for registered executables
    if os.name == "nt":
        try:
            import winreg
            key_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{clean_cmd}.exe"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path):
                return True
        except Exception:
            pass
        try:
            import winreg
            key_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{clean_cmd}.exe"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path):
                return True
        except Exception:
            pass

    # 4. Check Windows Registry HKCR for registered protocol handlers (e.g. microsoft.windows.camera:, ms-settings:, etc.)
    if os.name == "nt":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, clean_cmd):
                return True
        except Exception:
            pass

    # 5. Check common installation directories for actual executable binary
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
                return True

    return False

def is_app_available_with_retry(app_name: str, command: str, max_retries: int = 3, retry_delay: float = 0.3) -> bool:
    """Uses a Retry Mechanism to check if an application is available locally."""
    for attempt in range(1, max_retries + 1):
        app_logger.info(f"Local app check attempt {attempt}/{max_retries} for '{app_name}' (command: '{command}')")
        if check_local_app_availability(command):
            return True
        if check_local_app_availability(app_name):
            return True
        if attempt < max_retries:
            time.sleep(retry_delay)
    return False

def launch_in_chrome(url: str, app_mode: bool = True):
    """Launches a URL in Google Chrome using the Default user profile to prevent 'Who's using Chrome?' profile selector popups."""
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
    """Launches an installed desktop application or web platform by its natural language name."""
    app_logger.info(f"Executing launch_app tool for: {app_name}")
    name_clean = app_name.lower().strip()
    command = APP_MAP.get(name_clean, name_clean)
    display_name = name_clean.capitalize() if name_clean else "Application"

    # Priority 1: Web platform mapping (LinkedIn, YouTube, GitHub, ChatGPT, Google, Spotify, etc.)
    url = WEB_URL_MAP.get(name_clean)
    if url:
        if not is_cloud_environment():
            try:
                launch_in_chrome(url, app_mode=True)
            except Exception:
                pass
        return f"🌐 **Opened {display_name}**: [{url}]({url})"

    # Priority 2: Local desktop executable check
    available_locally = is_app_available_with_retry(name_clean, command, max_retries=3, retry_delay=0.1)

    if available_locally:
        if is_cloud_environment():
            return f"🚀 [ACTION:LAUNCH_APP:{command}] Successfully launched local application: '{display_name}'."
        try:
            shortcut = find_start_menu_shortcut(name_clean) or find_start_menu_shortcut(command)
            if shortcut and os.path.exists(shortcut):
                os.startfile(shortcut)
            elif os.name == "nt":
                clean_cmd = command[:-1] if command.endswith(":") else command
                cmd_path = shutil.which(clean_cmd) or shutil.which(f"{clean_cmd}.exe")
                if cmd_path and os.path.exists(cmd_path):
                    os.startfile(cmd_path)
                else:
                    subprocess.Popen(f'start "" "{command}"', shell=True)
            else:
                subprocess.Popen([command])
            return f"Successfully launched local application: '{display_name}'."
        except Exception as e:
            app_logger.warning(f"Failed to execute local app '{app_name}': {e}")

    if is_cloud_environment():
        return f"🚀 [ACTION:LAUNCH_APP:{command}] Successfully launched local application: '{display_name}'."

    return f"Application '{display_name}' not found locally."

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

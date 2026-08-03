from app.tools.utility_tools import calculator_tool, uuid_generator_tool, datetime_now_tool
from app.tools.search_tools import web_search_tool
from app.tools.filesystem_tools import read_file_tool, write_file_tool, list_dir_tool
from app.tools.python_tools import execute_python_tool
from app.tools.desktop_tools import launch_app_tool, list_running_apps_tool
from app.tools.system_tools import (
    get_system_stats_tool,
    take_screenshot_tool,
    lock_computer_tool,
    sleep_computer_tool,
    shutdown_computer_tool,
    restart_computer_tool,
)
from app.tools.media_tools import media_control_tool
from app.tools.communication_tools import draft_message_tool
from app.tools.weather_tools import get_weather_tool
from app.tools.news_tools import get_news_tool

ALL_TOOLS = [
    calculator_tool,
    uuid_generator_tool,
    datetime_now_tool,
    web_search_tool,
    read_file_tool,
    write_file_tool,
    list_dir_tool,
    execute_python_tool,
    launch_app_tool,
    list_running_apps_tool,
    get_system_stats_tool,
    take_screenshot_tool,
    lock_computer_tool,
    sleep_computer_tool,
    shutdown_computer_tool,
    restart_computer_tool,
    media_control_tool,
    draft_message_tool,
    get_weather_tool,
    get_news_tool,
]

TOOL_REGISTRY = {tool.name: tool for tool in ALL_TOOLS}

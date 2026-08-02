import pytest
from unittest.mock import patch
from app.tools.desktop_tools import (
    launch_app_tool,
    check_local_app_availability,
    is_app_available_with_retry,
    WEB_URL_MAP
)

def test_web_url_map_contains_popular_apps():
    assert "youtube" in WEB_URL_MAP
    assert "linkedin" in WEB_URL_MAP
    assert "whatsapp" in WEB_URL_MAP
    assert WEB_URL_MAP["youtube"] == "https://www.youtube.com"
    assert WEB_URL_MAP["linkedin"] == "https://www.linkedin.com"

def test_is_app_available_with_retry_true():
    with patch("app.tools.desktop_tools.check_local_app_availability", return_value=True) as mock_check:
        res = is_app_available_with_retry("calculator", "calc", max_retries=3, retry_delay=0.01)
        assert res is True
        assert mock_check.call_count >= 1

def test_is_app_available_with_retry_false():
    with patch("app.tools.desktop_tools.check_local_app_availability", return_value=False) as mock_check:
        res = is_app_available_with_retry("non_existent_app_xyz", "non_existent_app_xyz", max_retries=3, retry_delay=0.01)
        assert res is False
        assert mock_check.call_count == 6  # 2 checks per retry * 3 retries

def test_launch_app_tool_fallback_to_chrome():
    with patch("app.tools.desktop_tools.is_app_available_with_retry", return_value=False):
        with patch("subprocess.Popen") as mock_popen, patch("webbrowser.open") as mock_webopen:
            result = launch_app_tool.invoke({"app_name": "youtube"})
            assert "Opened 'Youtube' in Chrome" in result
            assert "https://www.youtube.com" in result

def test_launch_app_tool_local_success():
    with patch("app.tools.desktop_tools.is_app_available_with_retry", return_value=True):
        with patch("subprocess.Popen") as mock_popen:
            result = launch_app_tool.invoke({"app_name": "calculator"})
            assert "Successfully launched local application: 'Calculator'." in result

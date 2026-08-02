import pytest
from unittest.mock import patch
from app.agents.supervisor import supervisor_agent_node
from app.tools.media_tools import media_control_tool, adjust_volume_by_percentage
from app.tools.desktop_tools import find_start_menu_shortcut

@pytest.mark.asyncio
async def test_supervisor_routes_volume_to_media():
    state = {"user_query": "increase volume by 10%"}
    res = await supervisor_agent_node(state)
    assert res["next_agent"] == "media"
    assert res["intent"] == "media_control"

@pytest.mark.asyncio
async def test_supervisor_routes_mute_to_media():
    state = {"user_query": "mute sound"}
    res = await supervisor_agent_node(state)
    assert res["next_agent"] == "media"

def test_adjust_volume_percentage_extraction():
    with patch("ctypes.windll.user32.keybd_event"):
        res = adjust_volume_by_percentage("increase volume by 10%")
        assert "increased" in res
        assert "10%" in res

def test_find_start_menu_shortcut_notepad():
    shortcut = find_start_menu_shortcut("notepad")
    assert shortcut is not None
    assert shortcut.endswith(".lnk")

import pytest
from app.tools.weather_tools import get_weather_tool
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_get_weather_tool_direct():
    result = await get_weather_tool.ainvoke({"city": "London", "units": "metric"})
    assert "Weather in" in result or "not found" in result
    assert "London" in result

def test_weather_tool_in_tools_list():
    response = client.get("/tools")
    assert response.status_code == 200
    tools = response.json()
    assert any(t["name"] == "get_weather" for t in tools)

def test_weather_tool_endpoint_execution():
    response = client.post("/tool", json={
        "tool_name": "get_weather",
        "arguments": {"city": "Tokyo"}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "Tokyo" in data["outputs"]["result"]

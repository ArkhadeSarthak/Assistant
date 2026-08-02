import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "AURA AI" in data["service"]

def test_list_agents():
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert len(data["agents"]) > 0

def test_list_tools():
    response = client.get("/tools")
    assert response.status_code == 200
    tools = response.json()
    assert len(tools) > 0
    assert any(t["name"] == "calculator" for t in tools)

def test_calculator_tool_endpoint():
    response = client.post("/tool", json={
        "tool_name": "calculator",
        "arguments": {"expression": "10 + 5 * 2"}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "20" in data["outputs"]["result"]

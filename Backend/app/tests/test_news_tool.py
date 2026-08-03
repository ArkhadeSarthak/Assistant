import pytest
from app.tools.news_tools import get_news_tool, extract_news_query
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_extract_news_query():
    assert extract_news_query("news about AI") == "AI"
    assert extract_news_query("latest headlines on cricket") == "cricket"
    assert extract_news_query("give me news") in ["India", "news"]

@pytest.mark.asyncio
async def test_get_news_tool_direct():
    result = await get_news_tool.ainvoke({"query": "AI", "max_results": 5})
    assert "Top" in result or "No news" in result or "Unable to fetch" in result
    assert "AI" in result or "India" in result

def test_news_tool_in_tools_list():
    response = client.get("/tools")
    assert response.status_code == 200
    tools = response.json()
    assert any(t["name"] == "get_news" for t in tools)

def test_news_tool_endpoint_execution():
    response = client.post("/tool", json={
        "tool_name": "get_news",
        "arguments": {"query": "Technology", "max_results": 3}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "outputs" in data

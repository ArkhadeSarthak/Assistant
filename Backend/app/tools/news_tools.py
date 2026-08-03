import re
import httpx
from pydantic import BaseModel, Field
from langchain.tools import tool
from app.utils.logger import app_logger

GNEWS_API_KEY = "ee88cf0462144e13d368097cb0b4a2ba"
GNEWS_BASE_URL = "https://gnews.io/api/v4/search"

class NewsInput(BaseModel):
    query: str = Field(default="India", description="Topic or keyword to fetch news articles for (e.g., 'AI', 'Technology', 'Sports', 'Cricket', 'India')")
    max_results: int = Field(default=10, description="Maximum number of news articles to retrieve (default: 10)")
    country: str = Field(default="india", description="Country filter for news (e.g., 'india', 'us')")
    lang: str = Field(default="en", description="Language of the news articles (default: 'en')")

def extract_news_query(query: str) -> str:
    """Extracts target topic keyword from natural language news query."""
    if not query:
        return "India"
    
    query_clean = query.strip()
    
    # Pattern 1: "news about AI", "headlines on cricket", "latest news regarding tech"
    match = re.search(
        r'(?:news|headlines|updates|articles)\s+(?:about|on|regarding|for|of|in|related to)\s+([a-zA-Z0-9\s]+)',
        query_clean,
        re.IGNORECASE
    )
    if match:
        extracted = match.group(1).strip()
        cleaned = re.sub(r'\b(today|latest|india|recent|now)\b', '', extracted, flags=re.IGNORECASE).strip()
        if cleaned:
            return cleaned
        if extracted:
            return extracted

    # Pattern 2: "AI news", "tech headlines", "cricket updates"
    match = re.search(
        r'([a-zA-Z0-9\s]+)\s+(?:news|headlines|updates|articles)',
        query_clean,
        re.IGNORECASE
    )
    if match:
        extracted = match.group(1).strip()
        cleaned = re.sub(r'\b(get|show|tell|me|the|latest|today|find|fetch|give|some)\b', '', extracted, flags=re.IGNORECASE).strip()
        if cleaned:
            return cleaned
        if extracted:
            return extracted

    # Cleanup basic action verbs
    cleaned = re.sub(r'\b(get|show|tell|me|the|latest|today|find|fetch|give|some|news|headlines|updates|article|articles)\b', '', query_clean, flags=re.IGNORECASE).strip()
    return cleaned if len(cleaned) > 1 else "India"

@tool("get_news", args_schema=NewsInput)
async def get_news_tool(
    query: str = "India",
    max_results: int = 10,
    country: str = "india",
    lang: str = "en"
) -> str:
    """Fetches real-time breaking news articles using GNews API based on user topic or query."""
    search_query = extract_news_query(query) if len(query.split()) > 2 else query
    if not search_query or not search_query.strip():
        search_query = "India"

    app_logger.info(f"[NewsTool] Fetching news for query='{search_query}', max_results={max_results}, country={country}")
    
    params = {
        "q": search_query,
        "lang": lang,
        "country": country,
        "max": max_results,
        "apikey": GNEWS_API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(GNEWS_BASE_URL, params=params)
            
            if response.status_code != 200:
                app_logger.error(f"[NewsTool] GNews API error status {response.status_code}: {response.text}")
                return f"Unable to fetch news data (API HTTP status {response.status_code})."

            data = response.json()
            articles = data.get("articles", [])
            
            if not articles:
                # Retry with general query if specific query returned 0 results
                if search_query.lower() != "india":
                    app_logger.info(f"[NewsTool] No articles for '{search_query}', retrying with general query 'India'")
                    params["q"] = "India"
                    response = await client.get(GNEWS_BASE_URL, params=params)
                    if response.status_code == 200:
                        articles = response.json().get("articles", [])
                
            if not articles:
                return f"No news articles found for query '{search_query}'."

            formatted_articles = []
            for i, article in enumerate(articles[:max_results], 1):
                title = article.get("title", "No Title")
                description = article.get("description", "No Description")
                url = article.get("url", "#")
                published_at = article.get("publishedAt", "Unknown Date")
                source_name = article.get("source", {}).get("name", "GNews Source")
                
                entry = (
                    f"### {i}. [{title}]({url})\n"
                    f"- **Source:** {source_name} | **Published:** {published_at}\n"
                    f"- **Summary:** {description}\n"
                )
                formatted_articles.append(entry)

            result_text = f"Top {len(formatted_articles)} news updates for '{search_query}':\n\n" + "\n".join(formatted_articles)
            return result_text

    except httpx.TimeoutException:
        app_logger.error("[NewsTool] GNews API request timed out")
        return "Request timed out while fetching news updates."
    except Exception as e:
        app_logger.error(f"[NewsTool] Unexpected error: {e}")
        return f"Error fetching news articles: {str(e)}"

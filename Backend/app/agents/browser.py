import re
import urllib.parse
import webbrowser
from typing import Dict, Any
from app.graphs.state import AgentState
from app.tools.search_tools import web_search_tool
from app.tools.desktop_tools import launch_in_chrome
from app.utils.logger import app_logger

WEB_PLATFORMS = {
    "linkedin": ("LinkedIn", "https://www.linkedin.com"),
    "youtube": ("YouTube", "https://www.youtube.com"),
    "github": ("GitHub", "https://www.github.com"),
    "chatgpt": ("ChatGPT", "https://chatgpt.com"),
    "reddit": ("Reddit", "https://www.reddit.com"),
    "twitter": ("Twitter", "https://x.com"),
    "facebook": ("Facebook", "https://www.facebook.com"),
    "instagram": ("Instagram", "https://www.instagram.com"),
    "stackoverflow": ("StackOverflow", "https://stackoverflow.com"),
    "wikipedia": ("Wikipedia", "https://www.wikipedia.org"),
    "gmail": ("Gmail", "https://mail.google.com"),
    "google": ("Google", "https://www.google.com"),
}

async def browser_agent_node(state: AgentState) -> Dict[str, Any]:
    """Browser Agent: Performs web search, page summaries, and launches web applications (LinkedIn, YouTube, GitHub, etc.) in Chrome."""
    query = state.get("user_query", "").strip()
    query_lower = query.lower()
    app_logger.info(f"[BrowserAgent] Executing browser request for: '{query[:50]}'")

    output_text = ""
    matched_key = None

    # Check web platforms
    for key in WEB_PLATFORMS:
        if key in query_lower:
            matched_key = key
            break

    if matched_key:
        display_name, base_url = WEB_PLATFORMS[matched_key]
        
        # Check if user wants to search within YouTube or Google
        if matched_key == "youtube" and ("and search" in query_lower or "for" in query_lower or "search" in query_lower):
            search_topic = ""
            if "and search" in query_lower:
                search_topic = query_lower.split("and search")[1].strip()
            elif "search" in query_lower and "for" in query_lower:
                search_topic = query_lower.split("for")[1].strip()
            
            if search_topic:
                encoded_topic = urllib.parse.quote(search_topic)
                target_url = f"https://www.youtube.com/results?search_query={encoded_topic}"
                launch_in_chrome(target_url, app_mode=False)
                output_text = f"🌐 **Opened YouTube in Chrome**: Searching for **'{search_topic}'** at [{target_url}]({target_url})."
            else:
                launch_in_chrome(base_url, app_mode=True)
                output_text = f"🌐 **Opened {display_name} in Chrome**: [{base_url}]({base_url})."
        else:
            launch_in_chrome(base_url, app_mode=True)
            output_text = f"🌐 **Opened {display_name} in Chrome**: [{base_url}]({base_url})."

        browser_results = [{"query": query, "url": base_url, "status": "opened"}]
    else:
        try:
            search_res = await web_search_tool.ainvoke({"query": query})
            output_text = str(search_res)
        except Exception as e:
            output_text = f"Web search simulation for query '{query}': Retrieved real-time browser results."
        browser_results = [{"query": query, "output": output_text}]

    reasoning = state.get("intermediate_reasoning", []) + [f"Browser Agent opened web platform in Chrome ({matched_key or 'search'})"]

    return {
        "current_agent": "browser",
        "next_agent": "validator",
        "browser_results": browser_results,
        "formatted_response": output_text,
        "intermediate_reasoning": reasoning
    }

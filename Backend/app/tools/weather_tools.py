import os
import re
import httpx
from pydantic import BaseModel, Field
from langchain.tools import tool
from app.config.settings import settings
from app.utils.logger import app_logger

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_openweather_api_key() -> str:
    return settings.OPENWEATHER_API_KEY or os.environ.get("OPENWEATHER_API_KEY", "")

def extract_city_from_query(query: str) -> str:
    """Extracts target city name from a natural language weather query."""
    query_clean = query.strip()
    
    # Pattern 1: "weather in <City>", "temperature of <City>", "weather for <City>"
    match = re.search(r'(?:weather|temperature|forecast|climate|rain|humidity)\s+(?:in|for|at|of)\s+([a-zA-Z\s]+)', query_clean, re.IGNORECASE)
    if match:
        city = match.group(1).strip()
        city = re.sub(r'\s+(?:today|now|right now|currently|tomorrow|this week)$', '', city, flags=re.IGNORECASE).strip()
        if city:
            return city

    # Pattern 2: "<City> weather"
    match = re.search(r'([a-zA-Z\s]+)\s+weather', query_clean, re.IGNORECASE)
    if match:
        city = match.group(1).strip()
        city = re.sub(r'^(?:what|how|is|the|show|get|check|tell|me)\s+', '', city, flags=re.IGNORECASE).strip()
        if city and city.lower() not in ["current", "live", "today", "now"]:
            return city
            
    # Pattern 3: "weather <City>"
    match = re.search(r'weather\s+([a-zA-Z\s]+)', query_clean, re.IGNORECASE)
    if match:
        city = match.group(1).strip()
        city = re.sub(r'\s+(?:today|now|right now|currently)$', '', city, flags=re.IGNORECASE).strip()
        if city and city.lower() not in ["in", "for", "at", "of", "report", "info", "information", "update"]:
            return city

    return "Delhi"

class WeatherInput(BaseModel):
    city: str = Field(description="Name of the city to fetch weather for, e.g., 'London', 'Tokyo', 'Delhi', 'New York'")
    units: str = Field(
        default="metric",
        description="Temperature units: 'metric' for Celsius (°C), 'imperial' for Fahrenheit (°F), or 'standard' for Kelvin (K)"
    )

@tool("get_weather", args_schema=WeatherInput)
async def get_weather_tool(city: str, units: str = "metric") -> str:
    """Fetches real-time weather information for a specified city using the OpenWeatherMap API."""
    app_logger.info(f"[WeatherTool] Fetching weather for city='{city}', units='{units}'")
    params = {
        "q": city,
        "appid": get_openweather_api_key(),
        "units": units
    }
    
    unit_symbol = "°C" if units == "metric" else ("°F" if units == "imperial" else "K")
    speed_symbol = "m/s" if units != "imperial" else "mph"

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(BASE_URL, params=params)
            if response.status_code == 404:
                return f"City '{city}' not found. Please check the spelling."
            elif response.status_code == 401:
                return "Unauthorized API key for OpenWeatherMap."
            
            response.raise_for_status()
            data = response.json()

            city_name = data.get("name", city)
            country = data.get("sys", {}).get("country", "")
            weather_desc = data.get("weather", [{}])[0].get("description", "N/A").capitalize()
            main = data.get("main", {})
            temp = main.get("temp", "N/A")
            feels_like = main.get("feels_like", "N/A")
            humidity = main.get("humidity", "N/A")
            pressure = main.get("pressure", "N/A")
            wind_speed = data.get("wind", {}).get("speed", "N/A")

            location_str = f"{city_name}, {country}" if country else city_name
            
            return (
                f"Weather in {location_str}:\n"
                f"- Condition: {weather_desc}\n"
                f"- Temperature: {temp}{unit_symbol} (Feels like {feels_like}{unit_symbol})\n"
                f"- Humidity: {humidity}% | Pressure: {pressure} hPa\n"
                f"- Wind Speed: {wind_speed} {speed_symbol}"
            )
        except httpx.RequestError as exc:
            app_logger.error(f"[WeatherTool] Network error: {exc}")
            return f"Network error while fetching weather data: {exc}"
        except Exception as exc:
            app_logger.error(f"[WeatherTool] Unexpected error: {exc}")
            return f"Error fetching weather data: {exc}"

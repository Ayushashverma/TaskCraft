# external_apis.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def get_weather(city):
    if not OPENWEATHER_KEY:
        return "No OpenWeather key configured"
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": OPENWEATHER_KEY, "units": "metric"}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"{desc}, {temp}°C"
    except Exception as e:
        return f"Weather fetch error: {e}"

def web_search(query, num_results=3):
    if not SERPAPI_KEY:
        return ["No SerpAPI key configured"]
    try:
        url = "https://serpapi.com/search.json"
        params = {"q": query, "api_key": SERPAPI_KEY, "num": num_results}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        organic = data.get("organic_results") or data.get("organic", []) or []
        results = []
        for item in organic[:num_results]:
            title = item.get("title", "") 
            link = item.get("link") or item.get("url")
            if title and link:
                results.append(f"{title} — {link}")
            elif link:
                results.append(link)
        if not results:
            # fallback: use top search results if serpapi returns different shape
            for item in data.get("top_results", [])[:num_results]:
                results.append(item.get("link"))
        return results or ["No search results found"]
    except Exception as e:
        return [f"Search error: {e}"]

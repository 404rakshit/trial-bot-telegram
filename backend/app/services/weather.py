"""OpenWeatherMap API Integration

Handles fetching weather forecasts with caching to reduce API calls.
"""
import httpx
from typing import Optional, Dict, Any
from datetime import datetime
from app.core.config import settings
from app.core.session_store import save_weather_cache, get_weather_cache


def round_coordinates(lat: float, lon: float) -> tuple[float, float]:
    """Round coordinates to 2 decimal places (~1km grid) for caching

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Tuple of (rounded_lat, rounded_lon)
    """
    return (round(lat, 2), round(lon, 2))


def get_cache_key(lat: float, lon: float) -> str:
    """Generate cache key for weather data

    Args:
        lat: Latitude (should be rounded)
        lon: Longitude (should be rounded)

    Returns:
        Cache key string
    """
    return f"weather_{lat}_{lon}"


def fetch_weather_forecast(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Fetch 5-day weather forecast from OpenWeatherMap

    Uses caching to reduce API calls. Coordinates are rounded to ~1km grid.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Weather forecast data dict or None if error

    API Response Format:
        {
            "list": [
                {
                    "dt": 1234567890,  # Unix timestamp
                    "main": {"temp": 280.32, "pressure": 1012, "humidity": 81},
                    "weather": [{"id": 500, "main": "Rain", "description": "light rain"}],
                    "wind": {"speed": 4.1},
                    ...
                },
                ...
            ]
        }
    """
    if not settings.OPENWEATHER_API_KEY:
        print("⚠️  OpenWeatherMap API key not configured")
        return None

    # Round coordinates for caching
    lat, lon = round_coordinates(lat, lon)

    # Check cache first
    cache_key = get_cache_key(lat, lon)
    cached_data = get_weather_cache(cache_key)
    if cached_data:
        print(f"✅ Weather cache hit for {lat}, {lon}")
        return cached_data

    # Make API request
    try:
        url = f"{settings.OPENWEATHER_BASE_URL}/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": settings.OPENWEATHER_API_KEY,
            "units": "metric",  # Celsius
        }

        print(f"🌤️  Fetching weather for {lat}, {lon}...")
        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()

        data = response.json()

        # Cache the result
        save_weather_cache(cache_key, data, settings.WEATHER_CACHE_TTL)
        print(f"✅ Weather data cached for {lat}, {lon}")

        return data

    except httpx.HTTPError as e:
        print(f"❌ Error fetching weather: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def check_condition_in_forecast(
    forecast_data: Dict[str, Any],
    condition: str,
    hours_ahead: int
) -> bool:
    """Check if a weather condition will occur within the specified hours

    Args:
        forecast_data: Weather forecast data from API
        condition: Weather condition to check (e.g., "rain", "snow", "clear")
        hours_ahead: How many hours ahead to check

    Returns:
        True if condition will occur, False otherwise
    """
    if not forecast_data or "list" not in forecast_data:
        return False

    now = datetime.utcnow()
    target_time = now.timestamp() + (hours_ahead * 3600)

    # Normalize condition for comparison
    condition = condition.lower().strip()

    for forecast in forecast_data["list"]:
        forecast_time = forecast.get("dt", 0)

        # Check if this forecast is within our target time window
        # Allow some margin (±3 hours from target time)
        if abs(forecast_time - target_time) <= 3 * 3600:
            weather_list = forecast.get("weather", [])

            for weather in weather_list:
                main_condition = weather.get("main", "").lower()
                description = weather.get("description", "").lower()

                # Check if condition matches
                if condition in main_condition or condition in description:
                    return True

    return False


def get_weather_description(forecast_data: Dict[str, Any], hours_ahead: int) -> str:
    """Get a human-readable weather description for the specified time

    Args:
        forecast_data: Weather forecast data from API
        hours_ahead: How many hours ahead to check

    Returns:
        Weather description string
    """
    if not forecast_data or "list" not in forecast_data:
        return "Weather data unavailable"

    now = datetime.utcnow()
    target_time = now.timestamp() + (hours_ahead * 3600)

    # Find closest forecast
    closest_forecast = None
    min_diff = float('inf')

    for forecast in forecast_data["list"]:
        forecast_time = forecast.get("dt", 0)
        diff = abs(forecast_time - target_time)

        if diff < min_diff:
            min_diff = diff
            closest_forecast = forecast

    if not closest_forecast:
        return "No forecast available"

    # Extract weather info
    weather_list = closest_forecast.get("weather", [])
    if weather_list:
        description = weather_list[0].get("description", "Unknown")
        temp = closest_forecast.get("main", {}).get("temp", None)

        if temp is not None:
            return f"{description.capitalize()}, {temp:.1f}°C"
        return description.capitalize()

    return "Unknown conditions"

import httpx
from dotenv import load_dotenv

from config import settings

from .http_client import with_retry

load_dotenv()

accuweather_api_key = settings.accuweather_api_key


class WeatherData:
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    @with_retry()
    async def get_weather(self, location: str):

        async with httpx.AsyncClient(
            headers={"Authorization": f"Bearer {accuweather_api_key}"},
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=3),
            timeout=self.timeout,
        ) as client:
            try:
                key_response = await client.get(
                    url="https://dataservice.accuweather.com/locations/v1/cities/search",
                    headers={"Accept-Encoding": "gzip"},
                    params={"q": location},
                )

                key_response.raise_for_status()

            except httpx.TimeoutException as exc:
                raise httpx.TimeoutException(
                    f"Timeout fetching key for {location} after {self.timeout}s"
                ) from exc
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 401:
                    raise PermissionError("Invalid API key") from exc
                elif exc.response.status_code == 429:
                    raise httpx.HTTPStatusError(
                        "Rate limited by Accuweather.",
                        request=exc.request,
                        response=exc.response,
                    )
                else:
                    raise

            try:
                data = key_response.json()
            except ValueError as e:
                raise ValueError(
                    f"Invalid JSON response for location '{location}'"
                ) from e

            if not isinstance(data, list) or not data:
                raise ValueError(f"No location found for '{location}'")

            location_key = data[0].get("Key")
            if not location_key:
                raise ValueError(f"Location key missing for '{location}'")

            try:
                weather_response = await client.get(
                    url=f"https://dataservice.accuweather.com/currentconditions/v1/{location_key}"
                )

                weather_response.raise_for_status()

            except httpx.TimeoutException as e:
                raise httpx.TimeoutException(
                    f"Timeout fetching weather for location key '{location_key}' after {self.timeout}s"
                ) from e
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    raise httpx.HTTPStatusError(
                        "Rate limited by AccuWeather. Backing off.",
                        request=e.request,
                        response=e.response,
                    ) from e
                else:
                    raise
            except httpx.HTTPError as e:
                raise httpx.HTTPError(
                    f"Network error fetching weather data: {e}"
                ) from e
            try:
                weather_data = weather_response.json()
            except ValueError as e:
                raise ValueError("Invalid JSON response for weather data") from e

            if not isinstance(weather_data, list) or not weather_data:
                raise ValueError(
                    f"No weather data returned for location key '{location_key}'"
                )

            weather_item = weather_data[0]

            temp_metric = (weather_item.get("Temperature") or {}).get("Metric") or {}
            wind = weather_item.get("Wind") or {}
            wind_speed_metric = (wind.get("Speed") or {}).get("Metric") or {}

            return {
                "location": location,
                "weather_text": weather_item.get("WeatherText"),
                "has_precipitation": weather_item.get("HasPrecipitation"),
                "metric_temp": temp_metric.get("Value"),
            }

import logging

from fastmcp import FastMCP

from integrations.news_api import NewsApiClient
from integrations.weather_api import WeatherData

logger = logging.getLogger("mcp.tools")

info_mcp = FastMCP(name="Weather & News Tools")

news_api = NewsApiClient()
weather_api = WeatherData()


@info_mcp.tool()
async def get_news_by_category(category: str):
    """Fetch top headlines for a given news category.

    Args:
            category (str): The news category to fetch. Accepted: business, entertainment, general, health, science, sports, technology.
    """
    logger.info("get_news_by_category tool invoked")

    news = await news_api.get_news(
        endpoint="top-headlines", query_param="category", content=category
    )
    return news


@info_mcp.tool()
async def get_news_by_country(country: str):
    """Fetch top headlines for a given country code.

    Args:
        country (str): The accepted 2-letter country code (accepted country codes - ae, ar, at, au, be, bg, br, ca, ch, cn, co, cu, cz, de, eg, fr, gb, gr, hk, hu, id, ie, il, in, it, jp, kr, lt, lv, ma, mx, my, ng, nl, no, nz, ph, pl, pt, ro, rs, ru, sa, se, sg, sk, th, tr, tw, ua, us, ve, za).
    """
    logger.info("get_news_by_country tool invoked")

    news = await news_api.get_news(
        endpoint="top-headlines", query_param="country", content=country
    )
    return news


@info_mcp.tool()
async def get_news_by_topic(topic: str):
    """Fetch articles matching a specific topic keyword.

    Args:
        topic (str): A search keyword or phrase to search for articles.
    """
    logger.info("get_news_by_topic tool invoked")
    news = await news_api.get_news(
        endpoint="everything", query_param="q", content=topic
    )
    return news


@info_mcp.tool()
async def get_weather(location: str) -> dict:
    """Fetch weather text, precipitation status and temperature in celcius of any location

    Args:
         location (str): A location name - city, town etc.
    """
    logger.info("get_weather tool invoked")

    weather = await weather_api.get_weather(location=location)
    return weather

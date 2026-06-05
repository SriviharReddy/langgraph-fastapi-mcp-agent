
import httpx

from config import settings

from .http_client import with_retry

news_api_key = settings.news_api_key


class NewsApiClient:
    def _filter_articles(self, data: dict, limit: int = 5) -> list:
        raw_articles = data.get("articles", [])
        filtered = []
        for article in raw_articles:
            title = article.get("title")
            url = article.get("url")

            # Filter out missing, removed, or invalid articles
            if not title or title == "[Removed]" or not url:
                continue

            description = article.get("description") or ""
            content = article.get("content") or description

            # Clean and cap content to avoid context flood
            if content and len(content) > 200:
                content = content[:200] + "..."

            filtered.append(
                {
                    "title": title,
                    "url": url,
                    "description": description[:150] + "..."
                    if len(description) > 150
                    else description,
                    "content": content,
                }
            )
            if len(filtered) >= limit:
                break
        return filtered

    @with_retry()
    async def get_news(self, endpoint: str, query_param: str, content: str) -> list:
        async with httpx.AsyncClient(
            base_url="https://newsapi.org/v2",
            headers={"X-Api-Key": news_api_key},
            timeout=10.0,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=3),
        ) as client:
            response = await client.get(
                url=f"/{endpoint}", params={query_param: content, "language": "en"}
            )
            response.raise_for_status()
            return self._filter_articles(response.json())

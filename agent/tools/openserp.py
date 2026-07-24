import requests
from typing import Any

import requests
from typing import Any


class OpenSERPClient:

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def search(
        self,
        query: str,
        engine: str = "bing",
        limit: int = 10,
    ) -> dict[str, Any]:

        response = requests.get(
            f"{self.base_url}/{engine}/search",
            params={
                "text": query,
                "limit": limit,
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()

    def _normalize_search_results(
        self,
        response: dict[str, Any],
        max_results: int = 10,
    ) -> list[dict[str, str | None]]:

        normalized = []

        for item in response.get("results", []):

            # Only keep organic web results
            if item.get("type") != "organic":
                continue

            title = item.get("title")
            url = item.get("url")
            snippet = item.get("snippet")

            # Ignore malformed results
            if not title or not url:
                continue

            normalized.append({
                "title": title,
                "url": url,
                "snippet": snippet or "",
                "domain": item.get("domain"),
            })

            if len(normalized) >= max_results:
                break

        return normalized

    def _format_search_results(
        self,
        results: list[dict[str, str | None]],
    ) -> str:

        formatted = []

        for i, result in enumerate(results, start=1):

            formatted.append(
                f"{i}. {result['title']}\n"
                f"URL: {result['url']}\n"
                f"Snippet: {result['snippet']}"
            )

        return "\n\n".join(formatted)
    
    def search_for_agents(
            self,
            query: str,
            engine: str = "bing",
            limit: int = 10,
    ) -> str:
        response = self.search(
            query=query,
            engine=engine,
            limit=limit
        )
        results = self._normalize_search_results(response, max_results=limit)
        return self._format_search_results(results)
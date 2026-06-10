import logging
import re
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from news_aggregator.application.interfaces.feed_discovery import FeedDiscovery
from news_aggregator.infrastructure.ingestion.feed_parser import FeedparserFeedParser

logger = logging.getLogger(__name__)

FEED_LINK_PATTERN = re.compile(r"application/(rss\+xml|atom\+xml)", re.IGNORECASE)


class HtmlFeedDiscovery(FeedDiscovery):
    """Discover RSS/Atom feeds from direct feed URLs or HTML link tags."""

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        feed_parser: FeedparserFeedParser,
    ) -> None:
        self._http_client = http_client
        self._feed_parser = feed_parser

    async def discover_feed_url(self, source_url: str) -> str:
        """Discover a feed URL for the configured source."""
        if await self._feed_parser.is_valid_feed(source_url):
            logger.info("Source URL is a valid feed", extra={"source_url": source_url})
            return source_url

        response = await self._http_client.get(source_url, follow_redirects=True)
        response.raise_for_status()

        candidate_urls = self._extract_feed_links(response.text, str(response.url))
        for candidate_url in candidate_urls:
            if await self._feed_parser.is_valid_feed(candidate_url):
                logger.info(
                    "Discovered feed URL",
                    extra={"source_url": source_url, "feed_url": candidate_url},
                )
                return candidate_url

        msg = f"No RSS/Atom feed discovered for source: {source_url}"
        raise ValueError(msg)

    @staticmethod
    def _extract_feed_links(html: str, base_url: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        discovered: list[str] = []
        seen: set[str] = set()

        for link_tag in soup.find_all("link", href=True):
            rel = link_tag.get("rel")
            link_type = str(link_tag.get("type", ""))
            href = str(link_tag.get("href", "")).strip()

            if not href:
                continue

            rel_values = [value.lower() for value in rel] if isinstance(rel, list) else []
            if "alternate" not in rel_values:
                continue
            if not FEED_LINK_PATTERN.search(link_type):
                continue

            absolute_url = urljoin(base_url, href)
            if absolute_url in seen:
                continue

            seen.add(absolute_url)
            discovered.append(absolute_url)

        parsed_base = urlparse(base_url)
        for suffix in ("/feed", "/rss", "/rss.xml", "/atom.xml", "/feed.xml"):
            candidate = f"{parsed_base.scheme}://{parsed_base.netloc}{suffix}"
            if candidate not in seen:
                seen.add(candidate)
                discovered.append(candidate)

        return discovered

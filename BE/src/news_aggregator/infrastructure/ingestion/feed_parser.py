import asyncio
import logging

import feedparser

from news_aggregator.application.interfaces.feed_parser import FeedEntry, FeedParser

logger = logging.getLogger(__name__)


class FeedparserFeedParser(FeedParser):
    """feedparser-based implementation of FeedParser."""

    async def parse(self, feed_url: str) -> list[FeedEntry]:
        """Parse an RSS/Atom feed and return article URLs."""
        parsed = await asyncio.to_thread(feedparser.parse, feed_url)

        if parsed.bozo:
            logger.warning(
                "Feed parsed with warnings",
                extra={"feed_url": feed_url, "exception": str(parsed.bozo_exception)},
            )

        entries: list[FeedEntry] = []
        seen_urls: set[str] = set()

        for entry in parsed.entries:
            article_url = self._extract_entry_url(entry)
            if article_url is None or article_url in seen_urls:
                continue
            seen_urls.add(article_url)
            entries.append(FeedEntry(url=article_url))

        logger.info(
            "Feed parsed",
            extra={"feed_url": feed_url, "entry_count": len(entries)},
        )
        return entries

    async def is_valid_feed(self, feed_url: str) -> bool:
        """Return whether the URL points to a parseable feed with entries."""
        parsed = await asyncio.to_thread(feedparser.parse, feed_url)
        return bool(parsed.entries)

    @staticmethod
    def _extract_entry_url(entry: feedparser.FeedParserDict) -> str | None:
        link = entry.get("link")
        if isinstance(link, str) and link.strip():
            return link.strip()

        links = entry.get("links")
        if isinstance(links, list):
            for item in links:
                href = item.get("href") if hasattr(item, "get") else None
                if isinstance(href, str) and href.strip():
                    return href.strip()

        return None

import logging
import re

import httpx
from bs4 import BeautifulSoup, Tag

from news_aggregator.application.interfaces.content_extractor import ContentExtractor

logger = logging.getLogger(__name__)

REMOVED_TAGS = (
    "script",
    "style",
    "nav",
    "header",
    "footer",
    "aside",
    "noscript",
    "iframe",
    "form",
)
AD_CLASS_PATTERN = re.compile(r"(^|[-_])(ad|ads|advert|banner|promo)([-_]|$)", re.IGNORECASE)


class BeautifulSoupContentExtractor(ContentExtractor):
    """BeautifulSoup-based implementation of ContentExtractor."""

    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._http_client = http_client

    async def extract(self, article_url: str) -> str:
        """Download and extract readable text from an article page."""
        response = await self._http_client.get(article_url, follow_redirects=True)
        response.raise_for_status()

        text = self._extract_text(response.text)
        logger.info(
            "Article text extracted",
            extra={"article_url": article_url, "text_length": len(text)},
        )
        return text

    def _extract_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        for tag_name in REMOVED_TAGS:
            for tag in soup.find_all(tag_name):
                if isinstance(tag, Tag):
                    tag.decompose()

        for tag in soup.find_all(True):
            if not isinstance(tag, Tag):
                continue

            class_names = tag.get("class")
            if isinstance(class_names, list) and any(
                AD_CLASS_PATTERN.search(class_name) for class_name in class_names
            ):
                tag.decompose()
                continue

            role = tag.get("role")
            if isinstance(role, str) and role.lower() == "navigation":
                tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        return " ".join(text.split())

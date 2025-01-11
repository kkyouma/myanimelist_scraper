import time
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup

from myanimelist_scrapper.models import Media
from myanimelist_scrapper.storage import Storage


class MediaType(Enum):
    MANGA = "manga"
    ANIME = "anime"


@dataclass
class MediaConfig:
    """Configuration for different media types."""

    base_url: str
    items_per_page: int = 50
    rate_limit: float = 1.0  # Time to wait between request in seconds


class MediaScraper:
    """Main scraper class for extracting manga information."""

    CONFIGS: ClassVar = {
        MediaType.MANGA: MediaConfig("https://myanimelist.net/topmanga.php"),
        MediaType.ANIME: MediaConfig("https://myanimelist.net/topanime.php"),
    }

    def __init__(self, storage: Storage, media_type: MediaType) -> None:
        self.storage = storage
        self.session = requests.Session()  # Use same conection
        self.config = self.CONFIGS[media_type]
        self.media_type = media_type

        # Set up session headers to be more browser-like
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            },
        )

    def get_page_url(self, page: int = 1) -> str | None:
        """Generate URL for a specific page."""
        offset = (page - 1) * self.config.items_per_page
        return f"{self.config.base_url}?limit={offset}"

    def fetch_page(
        self,
        url: str,
        retries: int = 3,
        timeout: int = 5,
    ) -> str | None:
        """Fetch page content retry logic."""
        for attempt in range(retries):
            try:
                time.sleep(self.config.rate_limit)

                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()

            except requests.RequestException as e:
                if attempt == retries - 1:
                    print(f"Failed to fetch {url} after {retries} attempts: {e}")
                time.sleep(2**attempt)

            else:
                return response.text
        return None

    # def save_file(self, content: str, url: str | None) -> str | None:
    #     """Save page content to storage if storage is configured."""
    #     if not self.storage:
    #         return None
    #
    #     parsed_url = urlparse(url)
    #     params = parse_qs(parsed_url.query)
    #     limit = params.get("limit", ["0"])[0]
    #
    #     if "stats" in url:
    #         media_id = url.split("/")[-2]
    #         filename = f"{self.media_type.value}_stats_{media_id}.html"
    #
    #     else:
    #         filename = f"{self.media_type.value}_stats_{limit or 'default'}.html"
    #
    #     return self.storage.save_html(content, filename)

    def extract_stats(self, url: str) -> dict[str, int | str | list[str] | None]:
        content = self.fetch_page(url)

    def extract_media(html_content: str) -> list[Manga]:
        """Parse HTML and extract manga metadata."""
        soup = BeautifulSoup(html_content, "html.parser")

        selector = "a[class*='fs14 fw-b']"

        return [Media.from_soup_tag(media) for media in soup.select(selector)]

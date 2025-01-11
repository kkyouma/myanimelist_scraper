from dataclasses import dataclass
from enum import Enum
from typing import ClassVar

import requests
from bs4 import BeautifulSoup

from myanimelist_scrapper.models import Manga
from myanimelist_scrapper.storage import Storage


class MediaType(Enum):
    MANGA = "manga"
    ANIME = "anime"


@dataclass
class MediaConfig:
    """Configuration for different media types."""

    base_url: str
    items_per_page: int = 50


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

    def get_page_url(self, top_n: int) -> str:
        """Generate URL for a specific page."""
        return f"{self.config.base_url}?limit={top_n}"

    def extract_items(self, html_content: str) -> list[Media]:
        """Extract"""

    def fetch_page(self, url: str, timeout: int = 5) -> str:
        """Fetch and save html."""
        response = self.session.get(url, timeout=timeout)
        response.raise_for_status()

        filename = f"{url}.html"
        self.storage.save_html(response.text, filename)

        return response.text

    def extract_manga(self, html_content: str) -> list[Manga]:
        """Parse HTML and extract manga metadata."""
        soup = BeautifulSoup(html_content, "html.parser")

        selector = "a[class*='fs14 fw-b']"

        return [Manga.from_soup_tag(manga_item) for manga_item in soup.select(selector)]

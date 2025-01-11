import contextlib
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from myanimelist_scrapper.storage import Storage


class MediaType(Enum):
    MANGA = "manga"
    ANIME = "anime"


@dataclass
class ScrapingRange:
    """Configuration for controlling the scraping range."""

    start: int  # Starting position (1-based index)
    end: int  # Ending position (inclusive)

    @property
    def total_items(self) -> int:
        """Calculate total number of items to scrape."""
        return self.end - self.start + 1

    def get_pages(self, items_per_page: int) -> tuple[int, int]:
        """Calculate starting and ending pages based on items per page."""
        start_page = ((self.start - 1) // items_per_page) + 1
        end_page = ((self.end - 1) // items_per_page) + 1
        return start_page, end_page

    def get_page_slice(self, page: int, items_per_page: int) -> tuple[int, int]:
        """Calculate item range for a specific page."""
        page_start = (page - 1) * items_per_page + 1
        page_end = page * items_per_page
        # Adjust indices based on scraping range
        start_idx = max(0, self.start - page_start)
        end_idx = min(items_per_page, self.end - page_start + 1)
        return start_idx, end_idx


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

    def save_file(self, content: str, url: str | None) -> str | None:
        """Save page content to storage if storage is configured."""
        if not self.storage:
            return None

        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)
        limit = params.get("limit", ["0"])[0]

        if "stats" in url:
            media_id = url.split("/")[-2]
            filename = f"{self.media_type.value}_stats_{media_id}.html"

        else:
            filename = f"{self.media_type.value}_stats_{limit or 'default'}.html"

        return self.storage.save_html(content, filename)

    def extract_stats(self, url: str) -> dict[str, int | str | list[str] | None]:
        """Extract detailed statistic from media stat page."""
        content = self.fetch_page(url)
        if not content:
            return {}

        soup = BeautifulSoup(content, "html.parser")
        stats = {}

        for div in soup.select("div[class*='spaceit_pad']"):
            label = div.find("span", class_="dark_text")
            if not label:
                continue

            key = label.text.strip().rstrip(":").lower()
            links = div.find_all("a")

            # Get the text after the label and clean it
            if len(links) > 1:
                value = [link.text.strip() for link in links]
            elif len(links) == 1:
                value = links[0].text.strip()
            else:
                value = label.next_sibling.strip()

            if key in ["episodes", "members", "favorites"]:
                with contextlib.suppress(ValueError, TypeError):
                    value = int(str(value).replace(",", ""))

            stats[key] = value
            # print(f"{key}: {value}")

        return stats

    def extract_media_liist(
        self,
        html_content: str,
        start_idx: int,
        end_idx: int | None,
    ) -> list[tuple[str, str]]:
        """Extract list of media items with their URLs within specified range."""
        soup = BeautifulSoup(html_content, "html.parser")
        items = []

        for i, item in enumerate(soup.select("a[class*='fs14 fw-b']")):
            if i < start_idx:
                continue
            if end_idx is not None and i >= end_idx:
                break

            url = item["href"]
            name = item.text.strip()
            items.append((name, url))

        return items

    def scrape_range(
        self,
        start: int,
        end: int,
        save_html: bool = False,
        progress_callback: Callable | None = None,
    ) -> list[dict]:
        """Scrape items within a specific range.

        Args:
            start: Starting position (1-based index)
            end: Ending position (inclusive)
            save_html: Whether to save HTML content
            progress_callback: Optional callback function for progress updates

        """
        scraping_range = ScrapingRange(start, end)
        start_page, end_page = scraping_range.get_pages(self.config.items_per_page)
        all_items = []

        print(f"\nScraping items {start} to {end} (pages {start_page} to {end_page})")

        for page in range(start_page, end_page + 1):
            url = self.get_page_url(page)
            content = self.fetch_page(url)

            if not content:
                print(f"Failed to fetch page {page}")
                continue

            if save_html:
                self.save_page(content, url)

            # Get item slice for this page
            start_idx, end_idx = scraping_range.get_page_slice(
                page,
                self.config.items_per_page,
            )
            media_items = self.extract_media_list(content, start_idx, end_idx)

            # Fetch stats for each item
            for i, (name, url) in enumerate(media_items):
                stats_url = urljoin(url, "stats")
                current_item = (page - start_page) * self.config.items_per_page + i + 1
                print(
                    f"Fetching stats for: {name} ({current_item}/{scraping_range.total_items})",
                )

                stats = self.extract_stats(stats_url, save_html)
                if stats:
                    item_data = {
                        "name": name,
                        "url": url,
                        "stats_url": stats_url,
                        "rank": start + len(all_items),
                        **stats,
                    }
                    all_items.append(item_data)

                    if progress_callback:
                        progress_callback(current_item, scraping_range.total_items)

                time.sleep(self.config.rate_limit)

        return all_items

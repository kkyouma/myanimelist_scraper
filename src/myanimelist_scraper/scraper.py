import contextlib
import time
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.panel import Panel
from storage import Storage

console = Console()


class MediaType(Enum):
    """Define the possible scrapes."""

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
    rate_limit: float = 2.0  # Time to wait between request in seconds


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
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            },
        )

    def print_stats(self, name: str, stats: dict, rank: int) -> None:
        """Print extracted stats in a formatted way."""
        console.print(Panel(f"[bold cyan]#{rank} {name}[/bold cyan]"))

        # Group related stats for better readability
        groups = {
            "Basic Info": ["type", "status", "episodes", "chapters", "volumes"],
            "Dates": ["aired", "premiered", "broadcast", "published"],
            "Creators": ["producers", "licensors", "studios", "authors"],
            "Details": ["source", "genres", "demographic", "rating", "duration"],
            "Stats": ["score", "ranked", "popularity", "members", "favorites"],
        }

        for group, keys in groups.items():
            relevant_stats = {k: stats.get(k) for k in keys if k in stats}
            if relevant_stats:
                console.print(f"[yellow]{group}:[/yellow]")
                for key, value in relevant_stats.items():
                    if isinstance(value, list):
                        console.print(f"  [green]{key}:[/green] {', '.join(value)}")
                    else:
                        console.print(f"  [green]{key}:[/green] {value}")

        console.print()  # Empty line for spacing

    def extract_media_list(
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

                # Check if got a valid response
                if response.status_code == 200 and response.text:
                    return response.text

            except requests.RequestException as e:
                wait_time = 2**attempt
                console.print(
                    f"[yellow]Attempt {attempt + 1} \
                    failed: {e}. \
                    Waiting {wait_time}s...[/yellow]",
                )
                time.sleep(wait_time)
                if attempt == retries - 1:
                    console.print(
                        f"Failed to fetch {url} after {retries} attempts: {e}",
                    )
                    return None

        return None

    def scrape_range(
        self,
        start: int,
        end: int,
        save_csv: bool = True,
    ) -> list[dict]:
        """Scrap the page in the range.

        Main scraping method that follows the workflow:
        1. Fetch main page with media list
        2. Extract media items within range
        3. For each media, fetch and extract its detailed stats
        4. Save results to CSV
        """
        console.print(
            f"\n[bold magenta]Starting scrape of {self.media_type.value} items {start} to {end}[/bold magenta]",
        )

        # Calculate page number for the range
        page = ((start - 1) // self.config.items_per_page) + 1
        url = f"{self.config.base_url}?limit={(page-1) * self.config.items_per_page}"

        # Step 1: Fetch main page
        console.print(f"[blue]Fetching main page: {url}[/blue]")
        content = self.fetch_page(url)
        if not content:
            return []

        # Step 2: Extract media list
        start_idx = (start - 1) % self.config.items_per_page
        end_idx = start_idx + (end - start + 1)
        media_items = self.extract_media_list(content, start_idx, end_idx)

        # Step 3: Process each media item
        all_items = []
        for i, (name, url) in enumerate(media_items, start):
            console.print(f"\n[bold yellow]Processing #{i}: {name}[/bold yellow]")

            # Get stats URL and fetch details
            stats_url = urljoin(url, "stats")
            console.print(f"[dim]Fetching stats: {stats_url}[/dim]")

            stats = self.extract_stats(stats_url)
            if stats:
                item_data = {"name": name, "url": url, "rank": i, **stats}
                all_items.append(item_data)

        # Step 4: Save results
        # if save_csv and all_items:
        #     filename = f"{self.media_type.value}_top_{start}_to_{end}.csv"
        #     self.save_to_csv(all_items, filename)

        console.print(
            f"\n[bold green]Scraping completed! Total items scraped: {len(all_items)}[/bold green]",
        )
        return all_items

        return None

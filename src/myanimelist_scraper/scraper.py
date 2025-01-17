import random
import time

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from storage import Storage

console = Console()


class MediaScraper:
    """Main scraper class for extracting manga information."""

    SUCCESFUL_RESPONSE = 200  # Good response for request

    def __init__(
        self,
        url: str,
        storage: Storage,
        min_delay: float = 1,
        max_delay: float = 5,
    ) -> None:
        self.url = url
        self.storage = storage
        self.session = requests.Session()  # Use same conection

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
        self.min_delay = min_delay
        self.max_delay = max_delay

    # TODO:
    # 1. Change the `raw` parameter to a enum class
    # 2. Add start/end functionality
    def extract_items_list(self, raw: str) -> list[tuple[str, str]]:
        """Extract the media items of the current page to scrap."""
        soup = BeautifulSoup(raw, "html.parser")
        media_list = []

        for _i, item in enumerate(soup.select("a[class=hoverinfo_trigger]")):
            url = item["href"]
            name = item.text.strip()
            media_list.append((name, url))

        return media_list

    # TODO: add read pandas DataFrame functionality
    def extract_item_detail(
        self,
        raw: str,
    ) -> dict[str, int | str | list[str] | None]:
        """Extract the detailed data for an item."""
        # TODO: replace with Media class and their get_stats_url method
        soup = BeautifulSoup(raw, "html.parser")
        stats = {}

        for div in soup.select("div[class*='spaceit_pad']"):
            label = div.find("span", class_="dark_text")

            if label:
                key = label.text.strip().rstrip(":").lower()
                links = div.find_all("a")
                # Get the text after the label and clean it
                if len(links) > 1:
                    value = [link.text.strip() for link in links]
                elif len(links) == 1:
                    value = links[0].text.strip()
                else:
                    value = label.next_sibling.strip()
                stats[key] = value

        return stats

    def fetch_page(
        self,
        url: str,
        retries: int = 3,
        timeout: int = 5,
    ) -> str:
        """Fetch page content retry logic."""
        for attempt in range(retries):
            try:
                delay = random.uniform(self.min_delay, self.max_delay)  # noqa: S311
                time.sleep(delay)

                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()

                # Check if got a valid response
                if (
                    response.status_code == MediaScraper.SUCCESFUL_RESPONSE
                    and response.text
                ):
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

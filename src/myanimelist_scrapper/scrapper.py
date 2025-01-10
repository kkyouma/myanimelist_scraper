import requests
from bs4 import BeautifulSoup

from myanimelist_scrapper.models import Manga
from myanimelist_scrapper.storage import Storage

MANGA_LINK = "https://myanimelist.net/topmanga.php"
ANIME_LINK = "https://myanimelist.net/topanime.php"


class MangaScraper:
    """Main scraper class for extracting manga information."""

    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.session = requests.Session()  # Use same conection

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
        manga_list = []

        for link_tag in soup.select("a[class*='hoverinfo_trigger fs14 fw-b']"):
            try:

        return manga_list

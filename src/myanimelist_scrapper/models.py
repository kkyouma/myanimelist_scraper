from dataclasses import dataclass
from urllib.parse import urljoin

from bs4.element import BeautifulSoup


@dataclass
class Manga:
    """Represesnts a manga entry with its metadata."""

    name: str
    url: str

    @property
    def stats_url(self) -> str:
        """Get the stats page URL."""
        return urljoin(self.url, "stats")

    @classmethod
    def from_soup_tag(cls, link_tag: BeautifulSoup):
        """Create a Manga instance from a BeautifulSoup tag."""
        return cls(
            name=link_tag.text.strip(),
            url=link_tag.get("href"),
        )

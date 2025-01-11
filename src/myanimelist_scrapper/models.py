from dataclasses import dataclass
from urllib.parse import urljoin

from bs4.element import BeautifulSoup


class Media:
    """Base class for media items."""

    name: str
    url: str
    media_type: str 

    @property
    def stats_url(self) -> str:
        """Get url for the media stats (metadata)."""
        return urljoin(self.url, "stats")

    @property
    def characters_url(self) -> str:
        """Get url for the media characters."""
        return urljoin(self.url, "characters")

    @classmethod
    def from_soup_tag(cls, link_tag: BeautifulSoup):
        """Create a Manga instance from a BeautifulSoup tag."""
        return cls(
            name=link_tag.text.strip(),
            url=link_tag.get("href"),
        )


@dataclass
class Manga(Media):
    """Represesnts a manga entry with its metadata."""

    media_type = "Manga"


class Anime(Media):
    """Represents a anime entry with its metadata."""

    media_type = "Anime"

    @property
    def episodes():
        pass


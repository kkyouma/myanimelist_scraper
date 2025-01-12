from dataclasses import dataclass
from datetime import date
from urllib.parse import urljoin

from bs4 import BeautifulSoup


@dataclass
class Media:
    """Base class for media items."""

    name: str
    url: str
    media_type: str | None
    status: str | None
    description: str | None
    generes: list[str] | None
    themes: list[str] | None
    authors: str | list[str]
    demographic: list[str] | str | None
    score: float | None
    rank: int | None
    popularity: int | None
    members: int | None

    @property
    def stats_url(self) -> str:
        """Get url for the media stats (metadata)."""
        return urljoin(self.url, "stats")

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
    published: dict[str, date]
    volumes: int | str
    chapters: int | str
    serialization: str


class Anime(Media):
    """Represents a anime entry with its metadata."""

    media_type = "Anime"
    episodes: int | str
    aired: dict[str, date]
    premiered: date  # NOTE: change type if datetime dont support "fall 2023" format
    brodcast: date  # %A at %H:%M (%Z)
    producers: list[str]
    licensors: str | list[str]
    studios: str | list[str]
    source: str
    duration: int  # Duration in minutes
    rating: str

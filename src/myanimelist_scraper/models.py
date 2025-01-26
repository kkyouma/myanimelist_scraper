from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import urljoin


@dataclass
class Media:
    """Base class for media items."""

    name: str
    url: str
    last_scraped: datetime
    scraped: bool = False

    @property
    def stats_url(self) -> str:
        """Get url for the media stats (metadata)."""
        return urljoin(self.url, "stats")

    @property
    def update_last_scraped(self) -> None:
        """Get the last scraped."""
        self.last_scraped = datetime.now(tz=UTC)



# @dataclass
# class Manga(Media):
#     """Represesnts a manga entry with its metadata."""
#
#     media_type = "Manga"
#     published: dict[str, date]
#     volumes: int | str
#     chapters: int | str
#     serialization: str
#
#
# class Anime(Media):
#     """Represents a anime entry with its metadata."""
#
#     media_type = "Anime"
#     episodes: int | str
#     aired: dict[str, date]
#     premiered: date  # NOTE: change type if datetime dont support "fall 2023" format
#     brodcast: date  # %A at %H:%M (%Z)
#     producers: list[str]
#     licensors: str | list[str]
#     studios: str | list[str]
#     source: str
#     duration: int  # Duration in minutes
#     rating: str

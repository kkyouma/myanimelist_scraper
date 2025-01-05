from dataclasses import dataclass


@dataclass
class Manga:
    """Represesnts a manga entry with its metadata."""

    name: str
    url: str

    @classmethod
    def from_soup_tag(cls, link_tag):
        """Create a Manga instance from a BeautifulSoup tag."""
        return cls(
            name=link_tag.text.strip(),
            url=link_tag["href"],
        )

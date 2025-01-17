"""Main scrap module."""

from models import Anime, Manga, Media
from scraper import MediaScraper
from utils import name_formatter

__all__ = ["Anime", "Manga", "Media", "MediaScraper", "name_formatter"]

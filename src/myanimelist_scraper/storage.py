from pathlib import Path


class Storage:
    """Handle all file operations for the scraper."""

    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)
        self.raw_path = self.base_path / "data" / "raw"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create necesary directories if they dont exist."""
        self.raw_path.mkdir(parents=True, exist_ok=True)

    def save_html(self, content: str, filename: str) -> Path:
        """Save raw HTML content to file."""
        file_path = self.raw_path / filename
        with file_path.open("w", encoding="utf-8") as f:
            f.write(content)

        return file_path

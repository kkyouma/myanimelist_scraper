import json
from pathlib import Path

import pandas as pd


class Storage:
    """Handle all file operations for the scraper."""

    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)
        self.raw_path = self.base_path / "data" / "raw"
        self.scraped_path = self.base_path / "data" / "scraped"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create necesary directories if they dont exist."""
        self.raw_path.mkdir(parents=True, exist_ok=True)
        self.scraped_path.mkdir(parents=True, exist_ok=True)

    def save_html(self, content: str, filename: str) -> Path:
        """Save raw HTML content to file."""
        file_path = self.raw_path / filename
        with file_path.open("w", encoding="utf-8") as f:
            f.write(content)

        return file_path

    def save_csv(self, content: list[dict], filename: str) -> Path:
        """Save data extracted from the scrap."""
        file_path = self.scraped_path / filename

        try:
            df = pd.DataFrame(content)

            mode = "w"
            header = True

            if file_path.exists():
                mode = "a"
                header = False

            df.to_csv(
                file_path,
                index=False,
                encoding="utf-8",
                mode=mode,
                header=header,
            )

        except (ValueError, OSError) as e:
            msg = f"Failed to save CSV to {file_path}: {e}"
            raise OSError(msg) from e

        return file_path

    def read_html(self, filename: str) -> str:
        """Read raw HTML content from a file."""
        file_path = self.raw_path / filename
        if not file_path.exists():
            raise FileNotFoundError(file_path)
        with file_path.open("r", encoding="utf-8") as f:
            return f.read()

    def save_json(self, content: dict, filename: str) -> Path:
        """Save data as a JSON file."""
        file_path = self.scraped_path / self._sanitize_filename(filename)
        try:
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(content, f, indent=4)
        except OSError as e:
            msg = f"Failed to save JSON to {file_path}: {e}"
            raise OSError(msg) from e
        return file_path

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename to remove unsafe characters."""
        return "".join(
            c for c in filename if c.isalnum() or c in ("-", "_", ".")
        ).strip()

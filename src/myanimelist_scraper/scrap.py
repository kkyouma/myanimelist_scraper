import pprint
import time

from rich.console import Console
from rich.panel import Panel
from scraper import MediaScraper
from storage import Storage
from utils import name_formatter


def main():
    console = Console()
    # Initialize storage and scraper
    url = "https://myanimelist.net/topanime.php"
    storage = Storage("..")
    scraper = MediaScraper(storage=storage, url=url)

    raw_index = scraper.fetch_page(url)
    scraper.storage.save_html(content=raw_index, filename="index_50.html")

    media_items: list[dict] = []
    items_list = scraper.extract_items_list(raw=raw_index)

    for i, item in enumerate(items_list):
        if i >= 3:
            break

        time.sleep(1)
        name = item[0]
        item_url = item[1]
        filename = name_formatter(name) + ".html"

        raw_detail = scraper.fetch_page(url=item_url)
        save_path = scraper.storage.save_html(content=raw_detail, filename=filename)

        # Print name and save
        console.print(f"[green]Saved in {save_path}")
        console.print(Panel(name))

        item_detail = scraper.extract_item_detail(raw=raw_detail)

        # Print item data
        console.print(pprint.pformat(item_detail))

        # Append to final list
        media_items.append(item_detail)

    # csv_name = name_formatter("demo_data") + ".csv"
    # scraper.storage.save_csv(content=media_items, filename=csv_name)


if __name__ == "__main__":
    main()

from rich.console import Console
from rich.panel import Panel
from scraper import MediaScraper
from storage import Storage
from utils import name_formatter


def main():
    console = Console()
    # Initialize storage and scraper
    url = "https://myanimelist.net/topanime.php"
    storage = Storage("../../")
    scraper = MediaScraper(storage=storage, url=url)

    # raw_index = scraper.fetch_page(url)
    filename = "index.html"
    raw_index = scraper.storage.read_html(filename=filename)
    # scraper.storage.save_html(content=raw_index, filename=filename)

    media_items: list[dict] = []
    items_list = scraper.extract_items_list(raw=raw_index)

    for i, item in enumerate(items_list, 1):
        if i >= 21:
            break

        name = item[0]
        item_url = item[1]
        filename = name_formatter(name) + ".html"

        # raw_detail = scraper.fetch_page(url=item_url)
        raw_detail = scraper.storage.read_html(filename=filename)
        # save_path = scraper.storage.save_html(content=raw_detail, filename=filename)

        # Print name and save
        # console.print(f"[green]Saved in {save_path}")
        msg = f"{i}: {name}"
        console.print(Panel(msg))

        item_detail = scraper.extract_item_detail(raw=raw_detail)

        # Print item data
        # console.print(pprint.pformat(item_detail))

        # Append to final list
        media_items.append(item_detail)

    csv_name = name_formatter("demo_data") + ".csv"
    csv_path = scraper.storage.save_csv(content=media_items, filename=csv_name)
    print(f"Data saved in {csv_path}")


if __name__ == "__main__":
    main()

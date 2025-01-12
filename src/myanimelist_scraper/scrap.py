from scraper import MediaScraper, MediaType
from storage import Storage

# Initialize storage and scraper
storage = Storage("./data")
scraper = MediaScraper(storage, MediaType.ANIME)

# Scrape top 50 manga
results = scraper.scrape_range(8, 9, save_csv=False)

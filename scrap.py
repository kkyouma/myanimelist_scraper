from src.scraper import MediaScraper, MediaType

# Initialize scraper without storage
scraper = MediaScraper(None, MediaType.ANIME)


# With progress callback
def progress(current, total):
    print(f"Progress: {current}/{total} ({current/total*100:.1f}%)")


results = scraper.scrape_range(1, 5, save_html=False, progress_callback=progress)

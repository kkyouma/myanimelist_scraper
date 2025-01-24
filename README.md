# Anime Scraper Project

**Note:**  
🔧 _This is an early prototype version of the project. Core functionality is implemented, but many basic features are still under development. Use with caution!_

A web scraper designed to extract anime information from [MyAnimeList](https://myanimelist.net/). It fetches data from the top anime list and saves details in CSV format for analysis.

---

## Features

### Implemented

- **Basic scraping**: Extracts anime details (name, score, rank, etc.).
- **Data storage**: Saves raw HTML and structured CSV files.
- **Request delays**: Random delays between requests to reduce server load.
- **Rich console output**: Visual progress tracking with the `rich` library.

### Planned Improvements

- **Pagination support**: Toggle between pages to scrape beyond the first 20 entries.
- **Human-like behavior**: Random item selection and dynamic delays to mimic organic browsing.
- **Error recovery**: Resume interrupted scraping sessions.
- **Extended metadata**: Additional fields like score distribution, characters, and user reviews.

---

## Requirements

- Python 3.8+
- Libraries:
  - `requests`
  - `beautifulsoup4`
  - `pandas`
  - `rich`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/anime-scraper.git
   cd anime-scraper
   ```

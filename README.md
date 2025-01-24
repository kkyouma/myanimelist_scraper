# Anime Scraper Project

This project is a web scraper designed to extract anime information from [MyAnimeList](https://myanimelist.net/). It fetches data from the top anime list and saves the details in CSV format for further analysis or use.

## Features

- **Web Scraping**: Extracts anime details such as name, score, rank, and more from MyAnimeList.
- **Data Storage**: Saves the scraped data in both HTML and CSV formats.
- **Customizable Delays**: Implements random delays between requests to avoid overwhelming the server.
- **Rich Console Output**: Uses the `rich` library to provide a visually appealing console output.

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

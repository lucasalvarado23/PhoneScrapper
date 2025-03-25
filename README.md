# Phone Number Scraper

A Python script that extracts phone numbers from websites using their sitemap.xml.

## Features

- Scrapes phone numbers from all pages listed in a sitemap.xml
- Outputs results to a CSV file with URL and phone number pairs
- Rate limiting to avoid overwhelming servers
- Progress tracking with logging

## Requirements

- Python 3.x
- requests
- beautifulsoup4

## Installation

```bash
pip install requests beautifulsoup4
```

## Usage

```bash
python scrape_phone_numbers.py <sitemap_url>
```

Example:
```bash
python scrape_phone_numbers.py https://example.com/sitemap.xml
```

The script will create a CSV file named `domain_phone_numbers_timestamp.csv` containing all found phone numbers and their source URLs.

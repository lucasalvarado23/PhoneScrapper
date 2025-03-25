import requests
from bs4 import BeautifulSoup
import re
import csv
import logging
from datetime import datetime
import sys
import xml.etree.ElementTree as ET
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

# Phone number patterns
PHONE_PATTERN = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
PHONE_REGEX = re.compile(PHONE_PATTERN)

# Set headers to mimic a real browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Rate limiting settings
RATE_LIMIT = 1  # requests per second
last_request_time = {}

def rate_limit(domain: str):
    """Implement rate limiting per domain"""
    current_time = time.time()
    if domain in last_request_time:
        time_passed = current_time - last_request_time[domain]
        if time_passed < RATE_LIMIT:
            time.sleep(RATE_LIMIT - time_passed)
    last_request_time[domain] = time.time()

def get_sitemap_urls(sitemap_url: str) -> list:
    """Get all URLs from the sitemap"""
    try:
        response = requests.get(sitemap_url, headers=HEADERS)
        root = ET.fromstring(response.text)
        urls = [elem.text for elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        return urls
    except Exception as e:
        logging.error(f"Error fetching sitemap: {e}")
        return []

def extract_phone_numbers(url: str) -> list:
    """Extract phone numbers from a given URL"""
    try:
        domain = url.split('/')[2]
        rate_limit(domain)
        
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            logging.warning(f"Failed to fetch {url}: Status {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()
        
        # Find all phone numbers in the text
        numbers = PHONE_REGEX.findall(text)
        return [(url, number.strip()) for number in numbers]
        
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        return []

def main():
    if len(sys.argv) != 2:
        logging.error("Usage: python3 scrape_phone_numbers.py <sitemap_url>")
        return
        
    sitemap_url = sys.argv[1]
    
    if not sitemap_url.startswith("http"):
        logging.error("Invalid URL. Please include http:// or https://")
        return

    logging.info(f"🔍 Fetching URLs from sitemap: {sitemap_url}")
    urls = get_sitemap_urls(sitemap_url)

    if not urls:
        logging.error("No URLs found in the sitemap.")
        return

    logging.info(f"📄 Found {len(urls)} pages to scan.")
    
    # Create CSV file
    website_name = sitemap_url.split("/")[2].replace("www.", "")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"{website_name}_phone_numbers_{timestamp}.csv"
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'Phone Number'])  # Write header
        
        for i, url in enumerate(urls, 1):
            phone_numbers = extract_phone_numbers(url)
            for url, number in phone_numbers:
                writer.writerow([url, number])
            
            logging.info(f"Progress: {i}/{len(urls)} pages processed")

    logging.info(f"\n✅ Phone numbers saved to {csv_file}")

if __name__ == "__main__":
    main()

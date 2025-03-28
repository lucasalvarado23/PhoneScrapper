from flask import Flask, request, jsonify, send_file, render_template, Response
import os
from scrape_phone_numbers import extract_phone_numbers, get_sitemap_urls
import logging
from datetime import datetime
import csv
import json

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route('/')
def index():
    return render_template('index.html')

def generate_updates(sitemap_url):
    try:
        # Create a unique filename for this scraping session
        website_name = sitemap_url.split("/")[2].replace("www.", "")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{website_name}_phone_numbers_{timestamp}.csv"
        
        def send_message(message, success=None):
            data = {
                'message': message,
                'success': success
            }
            yield f"data: {json.dumps(data)}\n\n"
            logging.info(message)
        
        # Get URLs from sitemap
        send_message(f"🔍 Fetching URLs from sitemap: {sitemap_url}")
        urls = get_sitemap_urls(sitemap_url)
        
        if not urls:
            send_message("No URLs found in the sitemap.", False)
            return
        
        send_message(f"📄 Found {len(urls)} pages to scan.")
        
        # Create CSV file and write header
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Phone Number'])
            
            # Process each URL
            for i, url in enumerate(urls, 1):
                phone_numbers = extract_phone_numbers(url)
                for url, number in phone_numbers:
                    writer.writerow([url, number])
                send_message(f"Progress: {i}/{len(urls)} pages processed")
        
        send_message(f"\n✅ Phone numbers saved to {output_file}", True)
        
    except Exception as e:
        error_message = f'Error: {str(e)}'
        send_message(error_message, False)
        logging.error(error_message)

@app.route('/scrape')
def scrape():
    sitemap_url = request.args.get('url')
    
    if not sitemap_url:
        return jsonify({
            'success': False,
            'messages': ['Please provide a sitemap URL']
        }), 400
    
    if not sitemap_url.startswith("http"):
        return jsonify({
            'success': False,
            'messages': ['Invalid URL. Please include http:// or https://']
        }), 400
    
    return Response(generate_updates(sitemap_url), mimetype='text/event-stream')

@app.route('/download')
def download():
    try:
        # Get the most recent file
        files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not files:
            return jsonify({
                'success': False,
                'messages': ['No results file found']
            }), 404
        
        latest_file = max(files, key=os.path.getctime)
        return send_file(latest_file, as_attachment=True)
        
    except Exception as e:
        error_message = f'Error: {str(e)}'
        logging.error(error_message)
        return jsonify({
            'success': False,
            'messages': [error_message]
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5005) 
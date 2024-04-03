from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
from datetime import datetime

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize Firebase Admin SDK with service account key from environment variable
cred = credentials.Certificate(os.getenv("SERVICE_ACCOUNT_KEY_PATH"))
firebase_admin.initialize_app(cred)
db = firestore.client()

def scrape_sitemap(url):
    def extract_content(url):
        html = requests.get(url)
        if html.status_code == 200:
            soup = BeautifulSoup(html.content, 'html.parser')
            
            # Extracting title
            title_tag = soup.find('h1', class_='m-none color_dgray article-header__headline p_bottom-xxs')
            title = title_tag.text.strip() if title_tag else None
            
            # Extracting text
            text_tags = soup.find_all('p', class_='article-body__text article-body--padding color_dgray m-none')
            text = '\n'.join([tag.text.strip() for tag in text_tags]) if text_tags else None
            
            return {'title': title, 'text': text}
        else:
            print("Failed to retrieve linked page:", html.status_code)
            return {'title': None, 'text': None}

    html = requests.get(url)
    data = []

    if html.status_code == 200:
        soup = BeautifulSoup(html.content, 'xml')  # Use 'xml' parser for sitemap.xml
        loc_tags = soup.find_all('loc')

        for loc_tag in loc_tags:
            loc = loc_tag.text.strip()
            # Check if URL is from opb.org/article domain and does not contain the specified class
            if 'https://www.opb.org/article/' in loc:
                content = extract_content(loc)
                if 'm-none f_primary f_bold color_dgray article-header__subheadline' not in loc:
                    data.append({'link': loc, 'title': content['title'], 'text': content['text']})
    else:
        print("Failed to retrieve sitemap. Status code:", html.status_code)

    return data

def store_story(date, story):
    # Add story to Firestore under the specified date
    db.collection('stories').document(date).collection('stories').add(story)

@app.route('/api/data', methods=['GET'])
def get_data():
    sitemap_url = 'https://www.opb.org/arc/outboundfeeds/news-sitemap/?outputType=xml'
    scraped_data = scrape_sitemap(sitemap_url)

    # Get current date in the format MM-DD-YY
    current_date = datetime.now().strftime("%m-%d-%y")

    # Store each story in Firestore under the current date
    for story in scraped_data:
        store_story(current_date, story)

    return jsonify(scraped_data)

if __name__ == '__main__':
    app.run(debug=True)

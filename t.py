import feedparser
import requests
from bs4 import BeautifulSoup
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.media import UploadFile
from together import Together
import json
import cloudscraper
from requests_html import HTMLSession
import random
import os
import html
import re
# Constants
RSS_FEED_URL = os.getenv("RSS_FEED_URL")
WP_URL = os.getenv("WP_URL")
WP_USER = os.getenv("WP_USER")
WP_PASS =  os.getenv("WP_PASS")
SERP_API_KEY = os.getenv("SERP_API_KEY")
# Setup WP Client
wp_client = Client(WP_URL, WP_USER, WP_PASS)

# Together AI API Key
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# Initialize Together AI client
client = Together(api_key=TOGETHER_API_KEY)


# List of rotating User-Agents to bypass bot detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]

def rephrase_text(text, purpose="rephrase"):
    """
    Uses Together AI to rephrase content or generate an article with proper SEO in Hinglish.
    """
    if purpose == "rephrase":
        prompt = f"Rephrase this title in Hinglish (mix of Hindi & English, using casual tone):\n\n{text}"
    
    elif purpose == "article":
        prompt = f"""
        Convert the following text into a **well-structured SEO-friendly article** in Hinglish. 

        🔹 **Instructions for formatting:**  
        - Use **<h1>** for the main title.  
        - Use **<h2>** for main subheadings.  
        - Use **<h3>** for smaller sections.  
        - Use **<p>** for paragraphs.  
        - Use bullet points (**<ul><li>**) where needed for readability.  
        - **Expand the content** to **at least 500 words** for better engagement.  
        - Use a friendly, natural Hinglish tone.  

        **Text to convert:**
        {text}

        🔹 **Additional Enhancements:**  
        - Add **FAQs** at the end for more depth.  
        - Include a **conclusion** with a strong call-to-action (CTA).  
        - Ensure the content is **unique & engaging** for online readers.  

        🔹 **Fun Facts Section:**  
        - At the end of the article, add a **'Fun Facts'** section.  
        - Include **2-3 interesting and unique facts** about the player or team mentioned in the article.  
        - The Fun Facts section should be **at least 200-350 words** for more depth.  
        - Use **<h2> Fun Facts** as the heading for this section.  
        """

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    
    return response.choices[0].message.content.strip()

def extract_rss_content(entry):
    """Extracts the best available content from an RSS entry."""
    if hasattr(entry, 'content') and entry.content:
        return entry.content[0].value.strip()
    elif hasattr(entry, 'summary') and entry.summary:
        return entry.summary.strip()
    elif hasattr(entry, 'description') and entry.description:
        return entry.description.strip()
    return "No content available."

def fetch_rss_articles():
    """Fetch latest cricket articles from the RSS feed while bypassing bot detection."""
    print("Fetching RSS feed...")

    scraper = cloudscraper.create_scraper()  # Bypass bot protection
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://www.google.com/",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = scraper.get(RSS_FEED_URL, headers=headers, timeout=10)
        response.raise_for_status()  # Ensure valid response

        feed = feedparser.parse(response.text)  # Parse RSS data

        if not feed.entries:
            print("❌ No articles found in RSS feed.")
            return []

        articles = []
        with open("rss_extracted_content.txt", "w", encoding="utf-8") as file:
            for entry in feed.entries:
                if not entry or not isinstance(entry, dict):  # Skip empty or invalid entries
                    print("🚫 Skipping empty or malformed entry.")
                    continue

                title = entry.get("title", "No Title Found")
                link = entry.get("link") or (entry.get("links", [{}])[0].get("href"))  # Try alternative link source

                if not link:
                    print(f"🚫 Skipping entry with missing link: {entry}")
                    continue

                content = extract_rss_content(entry)  # Extract content from RSS feed

                # Save extracted content for manual verification
                file.write(f"Title: {title}\n")
                file.write(f"Link: {link}\n")
                file.write(f"Content: {content}\n")
                file.write("=" * 80 + "\n\n")  # Separator for readability

                articles.append({"title": title, "link": link, "content": content})

        print(f"✅ Found {len(articles)} cricket articles.")
        return articles

    except requests.RequestException as e:
        print(f"❌ Failed to fetch RSS feed: {e}")
        return []
    
def search_image(query):
    """Find an image using SERP API."""
    url = f"https://serpapi.com/search.json?q={query}&tbm=isch&api_key={SERP_API_KEY}"
    response = requests.get(url).json()
    return response['images_results'][0]['original'] if 'images_results' in response else None

def is_valid_image(image_path):
    """Check if the image file is valid and non-corrupt."""
    return os.path.exists(image_path) and os.path.getsize(image_path) > 5000  # Avoid tiny/corrupt images

def sanitize_filename(title, max_length=50):
    """Sanitize title to create a valid filename."""
    title = re.sub(r'[^\w\s-]', '', title)  # Remove special characters
    title = re.sub(r'\s+', '_', title.strip())  # Replace spaces with underscores
    return title[:max_length]  # Limit length to prevent Windows issues


def upload_to_wordpress(title, content, image_url):
    """Upload an article to WordPress with a valid image."""
    post = WordPressPost()
    post.title = title
    post.content = content
    post.post_status = 'publish'
    post.terms_names = {'category': ['Sports']}
    
    if image_url:
        try:
            img_data = requests.get(image_url, timeout=10).content  # Added timeout to avoid hanging requests
            image_filename = sanitize_filename(title) + ".jpg"
            
            with open(image_filename, "wb") as img_file:
                img_file.write(img_data)
            
            if is_valid_image(image_filename):
                with open(image_filename, "rb") as img_file:
                    data = {'name': image_filename, 'type': 'image/jpeg', 'bits': img_file.read()}
                    response = wp_client.call(UploadFile(data))
                    post.thumbnail = response['id']
            else:
                print(f"🚫 Image {image_filename} is invalid. Skipping article.")
                return False
        
        except requests.RequestException as e:
            print(f"❌ Failed to download image: {e}")
            return False
        except OSError as e:
            print(f"❌ File handling error: {e}")
            return False
    
    wp_client.call(NewPost(post))
    print(f"✅ Posted: {title}")
    return True

# Main Execution
articles = fetch_rss_articles()
for article in articles:
    original_title = article.get('title', '').strip()
    original_content = article.get('content', '').strip()

    if not original_title or not original_content:
        print("🚫 Skipping empty or malformed article.")
        continue

    print(f"\n🚀 Processing: {original_title}")

    # Rephrase Title & Content
    rephrased_title = rephrase_text(original_title, "rephrase")
    seo_article = rephrase_text(original_content, "article")

    # Search for image
    image_url = search_image(rephrased_title)
    
    if not upload_to_wordpress(rephrased_title, seo_article, image_url):
        print(f"🚫 Skipped article: {rephrased_title}")
    else:
        print(f"✅ Successfully posted: {rephrased_title}\n")
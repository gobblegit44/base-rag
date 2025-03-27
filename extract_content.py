import requests
import string
import re
import os
from bs4 import BeautifulSoup
from bs4.element import Comment
from readability import Document
from urllib.parse import urlparse
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def tag_visible(element):
    blacklist = ['style', 'label', '[document]', 'embed',
                 'noscript', 'header', 'html', 'iframe',
                 'meta', 'title', 'aside', 'footer',
                 'form', 'nav', 'head', 'link',
                 'br', 'input', 'script', 'figure']
    if element.parent.name in blacklist:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(html):
    try:
        soup = BeautifulSoup(html, 'lxml')
    except AttributeError as e:
        return None
    texts = soup.body.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return "\n".join(t.strip() for t in visible_texts)

def extract_main_content(url):
    """
    Extract the main article content from a webpage while filtering out ads, navigation,
    and other non-content elements. Returns clean English text content.
    """
    try:
        # Send a GET request to the URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()

        if response.status_code != 200:
            return "Failed to retrieve content"

        # Use readability to get main content
        doc = Document(response.text)
        cleaned_html = doc.summary()
        
        # Extract text using our helper function
        text_content = text_from_html(cleaned_html)
        
        if not text_content:
            return "No content found"

        # Clean up the text
        text_content = re.sub(r'\s+', ' ', text_content)  # Replace multiple spaces
        text_content = re.sub(r'\[\d+\]', '', text_content)  # Remove citation numbers
        text_content = re.sub(r'[^\x00-\x7F]+', '', text_content)  # Remove non-ASCII chars
        text_content = text_content.strip()

        # Split into paragraphs and filter out empty ones
        paragraphs = [p.strip() for p in text_content.split('\n') if p.strip()]
        
        # Split into individual lines for enumeration
        lines = []
        for paragraph in paragraphs:
            lines.extend(paragraph.split('. '))
            
        # Clean up lines and filter empty ones
        lines = [line.strip() for line in lines if line.strip()]
        
        # Join lines with single line breaks
        text_content = '\n'.join(lines)
        
        # Ensure consistent line breaks at start and end
        text_content = f"\n{text_content}\n"

        return text_content

    except requests.RequestException as e:
        return f"Error fetching the URL: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def save_to_file(content, url):
    """
    Save the extracted content to a text file with timestamp.
    """
    # Create a filename using timestamp and domain name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = urlparse(url).netloc
    filename = f"extracted_content_{domain}_{timestamp}.txt"
    
    # Create output directory if it doesn't exist
    output_dir = "extracted_content"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save the content to file
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"URL: {url}\n")
        f.write("=" * 50 + "\n\n")
        f.write(content)
    
    return filepath

def main():
    # Example usage
    url = input("Enter the website URL: ")
    content = extract_main_content(url)
    
    # Save to file
    filepath = save_to_file(content, url)
    print(f"\nContent has been saved to: {filepath}")

if __name__ == "__main__":
    main() 
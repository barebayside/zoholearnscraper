"""
Zoho Learn Scraper
Extracts structured educational content from Zoho Learn shared links including
chapters, articles, and images for AI-powered question generation and spaced repetition learning.
"""

import requests
import json
import re
import time
import os
import hashlib
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urljoin, urlparse
from pathlib import Path

# Selenium imports (optional)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class ZohoLearnScraper:
    """
    A web scraper for extracting structured educational content from Zoho Learn.
    Supports chapters, articles, images, and structured content for AI consumption.
    """

    def __init__(self, use_selenium: bool = True, headless: bool = True,
                 output_dir: str = "zoho_learn_output", user_agent: Optional[str] = None):
        """
        Initialize the ZohoLearnScraper.

        Args:
            use_selenium: Use Selenium WebDriver for JavaScript-heavy sites (recommended for Zoho)
            headless: Run browser in headless mode (no GUI)
            output_dir: Directory to save scraped content and images
            user_agent: Custom user agent string. If None, uses default.
        """
        self.use_selenium = use_selenium
        self.headless = headless
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

        # Initialize requests session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

        # Selenium driver (initialized on first use)
        self.driver = None

        if use_selenium and not SELENIUM_AVAILABLE:
            raise ImportError(
                "Selenium is not installed. Install with: pip install selenium webdriver-manager"
            )

        # Track downloaded images to avoid duplicates
        self.downloaded_images = {}

    def _init_selenium_driver(self):
        """Initialize Selenium WebDriver if not already initialized."""
        if self.driver is not None:
            return

        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument(f'user-agent={self.user_agent}')

        # Allow images for educational content
        chrome_options.add_argument('--disable-gpu')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)

    def scrape_book(self, url: str, wait_time: int = 5) -> Dict[str, Any]:
        """
        Scrape an entire Zoho Learn book from a shared link.

        Args:
            url: The URL of the Zoho Learn shared book
            wait_time: Time to wait for page to load (Selenium only)

        Returns:
            Dictionary containing the complete book structure with all content
        """
        print(f"Starting scrape of Zoho Learn book: {url}")

        try:
            # Initialize the book structure
            book_data = {
                'url': url,
                'scraped_at': datetime.utcnow().isoformat(),
                'title': None,
                'description': None,
                'chapters': [],
                'metadata': {
                    'total_chapters': 0,
                    'total_articles': 0,
                    'total_images': 0,
                    'scraper_version': '1.0',
                    'spaced_repetition_ready': True
                }
            }

            # Get the main page
            if self.use_selenium:
                soup = self._scrape_with_selenium(url, wait_time)
            else:
                soup = self._scrape_with_requests(url)

            # Extract book metadata
            book_data['title'] = self._extract_book_title(soup)
            book_data['description'] = self._extract_book_description(soup)

            print(f"Book title: {book_data['title']}")

            # Extract table of contents
            toc = self._extract_table_of_contents(soup, url)

            print(f"Found {len(toc)} chapters")

            # Scrape each chapter and its articles
            for chapter_idx, chapter_info in enumerate(toc, 1):
                print(f"\nProcessing Chapter {chapter_idx}/{len(toc)}: {chapter_info['title']}")

                chapter_data = {
                    'chapter_number': chapter_idx,
                    'title': chapter_info['title'],
                    'articles': []
                }

                # Scrape each article in the chapter
                for article_idx, article_info in enumerate(chapter_info['articles'], 1):
                    print(f"  Processing Article {article_idx}/{len(chapter_info['articles'])}: {article_info['title']}")

                    article_data = self._scrape_article(
                        article_info['url'],
                        article_info['title'],
                        chapter_idx,
                        article_idx,
                        wait_time
                    )

                    chapter_data['articles'].append(article_data)

                    # Be respectful to the server
                    time.sleep(1)

                book_data['chapters'].append(chapter_data)

            # Update metadata
            book_data['metadata']['total_chapters'] = len(book_data['chapters'])
            book_data['metadata']['total_articles'] = sum(
                len(chapter['articles']) for chapter in book_data['chapters']
            )
            book_data['metadata']['total_images'] = len(self.downloaded_images)

            print(f"\n✓ Scraping complete!")
            print(f"  Total chapters: {book_data['metadata']['total_chapters']}")
            print(f"  Total articles: {book_data['metadata']['total_articles']}")
            print(f"  Total images: {book_data['metadata']['total_images']}")

            return book_data

        except Exception as e:
            print(f"Error scraping book: {str(e)}")
            return {
                'error': f'Error processing book: {str(e)}',
                'url': url,
                'scraped_at': datetime.utcnow().isoformat()
            }

    def _scrape_with_requests(self, url: str) -> BeautifulSoup:
        """Scrape using simple HTTP requests."""
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'lxml')

    def _scrape_with_selenium(self, url: str, wait_time: int = 5) -> BeautifulSoup:
        """Scrape using Selenium WebDriver."""
        self._init_selenium_driver()
        self.driver.get(url)

        # Wait for page to load
        time.sleep(wait_time)

        # Try to wait for content to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except:
            pass

        # Get page source after JavaScript execution
        page_source = self.driver.page_source
        return BeautifulSoup(page_source, 'lxml')

    def _extract_book_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the book title from the page."""
        selectors = [
            ('h1', {'class': re.compile(r'book.*title|title', re.I)}),
            ('h1', {}),
            ('title', {}),
            ('meta', {'property': 'og:title'}),
        ]

        for tag, attrs in selectors:
            if tag == 'meta':
                element = soup.find(tag, attrs)
                if element and element.get('content'):
                    return element['content'].strip()
            else:
                element = soup.find(tag, attrs)
                if element and element.get_text(strip=True):
                    title = element.get_text(strip=True)
                    # Clean up title
                    title = re.sub(r'\s*-\s*Zoho\s+Learn.*$', '', title, flags=re.I)
                    return title

        return "Untitled Book"

    def _extract_book_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the book description."""
        selectors = [
            ('meta', {'name': 'description'}),
            ('meta', {'property': 'og:description'}),
            ('div', {'class': re.compile(r'description|summary', re.I)}),
            ('p', {'class': re.compile(r'description|summary', re.I)}),
        ]

        for tag, attrs in selectors:
            if tag == 'meta':
                element = soup.find(tag, attrs)
                if element and element.get('content'):
                    return element['content'].strip()
            else:
                element = soup.find(tag, attrs)
                if element and element.get_text(strip=True):
                    return element.get_text(strip=True)

        return None

    def _extract_table_of_contents(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract the table of contents structure with chapters and articles."""
        toc = []

        # Look for common TOC patterns in Zoho Learn
        # Try multiple selectors to find the table of contents
        toc_selectors = [
            ('div', {'class': re.compile(r'toc|table.*of.*contents|sidebar|navigation', re.I)}),
            ('nav', {'class': re.compile(r'toc|navigation|sidebar', re.I)}),
            ('aside', {'class': re.compile(r'toc|navigation|sidebar', re.I)}),
            ('ul', {'class': re.compile(r'chapter|article.*list', re.I)}),
        ]

        toc_container = None
        for tag, attrs in toc_selectors:
            toc_container = soup.find(tag, attrs)
            if toc_container:
                break

        if not toc_container:
            # Fallback: look for any navigation structure
            toc_container = soup.find('nav') or soup.find('aside') or soup

        # Extract chapters and articles
        # Look for chapter headings and their associated articles
        chapters = []

        # Method 1: Find chapter-like headings followed by lists of articles
        headings = toc_container.find_all(['h2', 'h3', 'h4', 'div', 'li'],
                                          class_=re.compile(r'chapter|section|heading', re.I))

        for heading in headings:
            chapter_title = heading.get_text(strip=True)
            if not chapter_title:
                continue

            chapter = {
                'title': chapter_title,
                'articles': []
            }

            # Find articles under this chapter
            # Look for sibling lists or nested elements
            next_element = heading.find_next_sibling()

            # Try to find a list of articles
            article_list = None
            if next_element and next_element.name in ['ul', 'ol']:
                article_list = next_element
            else:
                # Look for nested lists
                article_list = heading.find('ul') or heading.find('ol')

            if article_list:
                links = article_list.find_all('a', href=True)
                for link in links:
                    article_url = urljoin(base_url, link['href'])
                    article_title = link.get_text(strip=True)

                    if article_title and article_url:
                        chapter['articles'].append({
                            'title': article_title,
                            'url': article_url
                        })

            if chapter['articles']:
                chapters.append(chapter)

        # Method 2: If no chapters found, treat all links as a single chapter
        if not chapters:
            all_links = toc_container.find_all('a', href=True)

            if all_links:
                chapter = {
                    'title': 'Main Content',
                    'articles': []
                }

                for link in all_links:
                    article_url = urljoin(base_url, link['href'])
                    article_title = link.get_text(strip=True)

                    # Filter out navigation links, external links, etc.
                    if (article_title and article_url and
                        not article_url.startswith('#') and
                        'zoho' in article_url.lower()):

                        chapter['articles'].append({
                            'title': article_title,
                            'url': article_url
                        })

                if chapter['articles']:
                    chapters.append(chapter)

        # Remove duplicate articles
        for chapter in chapters:
            seen_urls = set()
            unique_articles = []
            for article in chapter['articles']:
                if article['url'] not in seen_urls:
                    seen_urls.add(article['url'])
                    unique_articles.append(article)
            chapter['articles'] = unique_articles

        return chapters

    def _scrape_article(self, url: str, title: str, chapter_num: int,
                       article_num: int, wait_time: int = 5) -> Dict[str, Any]:
        """Scrape a single article page."""
        try:
            # Get the article page
            if self.use_selenium:
                soup = self._scrape_with_selenium(url, wait_time)
            else:
                soup = self._scrape_with_requests(url)

            # Extract article content
            article_data = {
                'article_number': article_num,
                'title': title,
                'url': url,
                'content': {
                    'structured': [],  # Structured content with headings, paragraphs, lists, etc.
                    'images': [],
                    'raw_text': '',
                },
                'metadata': {
                    'chapter_number': chapter_num,
                    'word_count': 0,
                    'estimated_reading_time_minutes': 0,
                    'spaced_repetition_metadata': {
                        'initial_interval_days': 1,
                        'suggested_intervals': [1, 3, 7, 14, 30, 60, 120],  # SM-2 inspired
                        'difficulty_estimate': 'medium',
                        'content_type': 'educational_article'
                    }
                }
            }

            # Find the main content area
            content_area = self._find_article_content(soup)

            if content_area:
                # Extract structured content
                article_data['content']['structured'] = self._extract_structured_content(
                    content_area, url
                )

                # Extract images
                article_data['content']['images'] = self._extract_and_download_images(
                    content_area, url, chapter_num, article_num
                )

                # Extract raw text for word count
                article_data['content']['raw_text'] = content_area.get_text(separator=' ', strip=True)

                # Calculate metadata
                words = article_data['content']['raw_text'].split()
                article_data['metadata']['word_count'] = len(words)
                article_data['metadata']['estimated_reading_time_minutes'] = max(1, len(words) // 200)

                # Estimate difficulty based on content length and structure
                if len(words) < 300:
                    article_data['metadata']['spaced_repetition_metadata']['difficulty_estimate'] = 'easy'
                elif len(words) > 1000:
                    article_data['metadata']['spaced_repetition_metadata']['difficulty_estimate'] = 'hard'

            return article_data

        except Exception as e:
            print(f"    Error scraping article: {str(e)}")
            return {
                'article_number': article_num,
                'title': title,
                'url': url,
                'error': str(e),
                'content': {'structured': [], 'images': [], 'raw_text': ''},
                'metadata': {'chapter_number': chapter_num}
            }

    def _find_article_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Find the main content area of an article."""
        content_selectors = [
            ('article', {}),
            ('div', {'class': re.compile(r'content|article|main|body', re.I)}),
            ('main', {}),
            ('div', {'id': re.compile(r'content|article|main', re.I)}),
            ('section', {'class': re.compile(r'content|article', re.I)}),
        ]

        for tag, attrs in content_selectors:
            content = soup.find(tag, attrs)
            if content:
                return content

        # Fallback: return body
        return soup.find('body')

    def _extract_structured_content(self, content_area: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract structured content preserving headings, paragraphs, lists, code blocks, etc."""
        structured_content = []

        # Process all content elements in order
        for element in content_area.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre', 'code', 'blockquote', 'table']):

            # Skip empty elements
            text = element.get_text(strip=True)
            if not text:
                continue

            element_data = {}

            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                element_data = {
                    'type': 'heading',
                    'level': int(element.name[1]),
                    'text': text
                }

            elif element.name == 'p':
                element_data = {
                    'type': 'paragraph',
                    'text': text
                }

            elif element.name in ['ul', 'ol']:
                items = [li.get_text(strip=True) for li in element.find_all('li', recursive=False)]
                element_data = {
                    'type': 'list',
                    'list_type': 'unordered' if element.name == 'ul' else 'ordered',
                    'items': items
                }

            elif element.name in ['pre', 'code']:
                element_data = {
                    'type': 'code',
                    'text': element.get_text(strip=False),
                    'language': element.get('class', [''])[0] if element.get('class') else None
                }

            elif element.name == 'blockquote':
                element_data = {
                    'type': 'quote',
                    'text': text
                }

            elif element.name == 'table':
                element_data = {
                    'type': 'table',
                    'html': str(element),
                    'text': text
                }

            if element_data:
                structured_content.append(element_data)

        return structured_content

    def _extract_and_download_images(self, content_area: BeautifulSoup, base_url: str,
                                     chapter_num: int, article_num: int) -> List[Dict[str, Any]]:
        """Extract and download images from the content."""
        images_data = []

        # Find all images
        images = content_area.find_all('img')

        for img_idx, img in enumerate(images, 1):
            src = img.get('src') or img.get('data-src')

            if not src:
                continue

            # Make absolute URL
            img_url = urljoin(base_url, src)

            # Get alt text and caption
            alt_text = img.get('alt', '')
            title = img.get('title', '')

            # Download the image
            local_path = self._download_image(img_url, chapter_num, article_num, img_idx)

            image_data = {
                'url': img_url,
                'local_path': str(local_path) if local_path else None,
                'alt_text': alt_text,
                'title': title,
                'caption': self._find_image_caption(img)
            }

            images_data.append(image_data)

        return images_data

    def _find_image_caption(self, img_element) -> Optional[str]:
        """Try to find a caption for an image."""
        # Look for figcaption
        parent = img_element.parent
        if parent and parent.name == 'figure':
            caption = parent.find('figcaption')
            if caption:
                return caption.get_text(strip=True)

        # Look for nearby text that might be a caption
        next_sibling = img_element.find_next_sibling()
        if next_sibling and next_sibling.name in ['p', 'div', 'span']:
            text = next_sibling.get_text(strip=True)
            if len(text) < 200:  # Likely a caption
                return text

        return None

    def _download_image(self, img_url: str, chapter_num: int,
                       article_num: int, img_idx: int) -> Optional[Path]:
        """Download an image and save it locally."""
        try:
            # Check if already downloaded
            if img_url in self.downloaded_images:
                return self.downloaded_images[img_url]

            # Download the image
            response = self.session.get(img_url, timeout=30)
            response.raise_for_status()

            # Determine file extension
            content_type = response.headers.get('content-type', '')
            ext = '.jpg'  # default
            if 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            elif 'svg' in content_type:
                ext = '.svg'
            elif 'webp' in content_type:
                ext = '.webp'

            # Generate filename
            filename = f"ch{chapter_num}_art{article_num}_img{img_idx}{ext}"
            filepath = self.images_dir / filename

            # Save the image
            with open(filepath, 'wb') as f:
                f.write(response.content)

            # Track downloaded image
            self.downloaded_images[img_url] = filepath

            return filepath

        except Exception as e:
            print(f"      Error downloading image {img_url}: {str(e)}")
            return None

    def save_to_json(self, book_data: Dict[str, Any], filename: Optional[str] = None):
        """
        Save scraped book data to a JSON file.

        Args:
            book_data: The scraped book data dictionary
            filename: Output filename (if None, generates from book title)
        """
        if filename is None:
            # Generate filename from book title
            title = book_data.get('title', 'zoho_learn_book')
            safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            filename = f"{safe_title}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(book_data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Data saved to: {output_path}")
        return output_path

    def save_for_ai_training(self, book_data: Dict[str, Any], filename: Optional[str] = None):
        """
        Save book data in a format optimized for AI question generation.
        Creates a simplified structure focused on content and context.

        Args:
            book_data: The scraped book data dictionary
            filename: Output filename (if None, generates from book title)
        """
        if filename is None:
            title = book_data.get('title', 'zoho_learn_book')
            safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            filename = f"{safe_title}_ai_ready_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

        # Create AI-optimized structure
        ai_data = {
            'book_title': book_data.get('title'),
            'book_description': book_data.get('description'),
            'scraped_at': book_data.get('scraped_at'),
            'learning_units': []
        }

        # Convert chapters and articles to learning units
        for chapter in book_data.get('chapters', []):
            for article in chapter.get('articles', []):

                # Combine structured content into readable text
                content_text = []
                for item in article['content']['structured']:
                    if item['type'] == 'heading':
                        content_text.append(f"\n{'#' * item['level']} {item['text']}\n")
                    elif item['type'] == 'paragraph':
                        content_text.append(item['text'])
                    elif item['type'] == 'list':
                        for list_item in item['items']:
                            prefix = '•' if item['list_type'] == 'unordered' else '1.'
                            content_text.append(f"{prefix} {list_item}")
                    elif item['type'] == 'code':
                        content_text.append(f"\n```\n{item['text']}\n```\n")
                    elif item['type'] == 'quote':
                        content_text.append(f"\n> {item['text']}\n")

                learning_unit = {
                    'id': f"ch{chapter['chapter_number']}_art{article['article_number']}",
                    'chapter': chapter['title'],
                    'chapter_number': chapter['chapter_number'],
                    'title': article['title'],
                    'content': '\n'.join(content_text),
                    'structured_content': article['content']['structured'],
                    'images': article['content']['images'],
                    'metadata': {
                        'word_count': article['metadata']['word_count'],
                        'estimated_reading_time_minutes': article['metadata']['estimated_reading_time_minutes'],
                        'difficulty': article['metadata']['spaced_repetition_metadata']['difficulty_estimate'],
                        'spaced_repetition_intervals': article['metadata']['spaced_repetition_metadata']['suggested_intervals'],
                    },
                    'context': {
                        'previous_chapter': chapter['title'] if chapter['chapter_number'] > 1 else None,
                        'source_url': article['url']
                    }
                }

                ai_data['learning_units'].append(learning_unit)

        # Add summary statistics
        ai_data['summary'] = {
            'total_learning_units': len(ai_data['learning_units']),
            'total_chapters': book_data['metadata']['total_chapters'],
            'total_images': book_data['metadata']['total_images'],
            'total_words': sum(unit['metadata']['word_count'] for unit in ai_data['learning_units']),
            'estimated_total_reading_time_minutes': sum(
                unit['metadata']['estimated_reading_time_minutes'] for unit in ai_data['learning_units']
            )
        }

        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(ai_data, f, indent=2, ensure_ascii=False)

        print(f"✓ AI-ready data saved to: {output_path}")
        return output_path

    def close(self):
        """Clean up resources (close Selenium driver if active)."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - clean up resources."""
        self.close()


def main():
    """Example usage of the ZohoLearnScraper."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python zoho_learn_scraper.py <zoho_learn_url>")
        print("\nExample:")
        print("  python zoho_learn_scraper.py https://learn.zoho.com/portal/yourorg/shared/book123")
        sys.exit(1)

    url = sys.argv[1]

    print("=" * 60)
    print("Zoho Learn Scraper - Educational Content Extractor")
    print("=" * 60)
    print()

    # Create scraper instance
    with ZohoLearnScraper(use_selenium=True, headless=True) as scraper:
        # Scrape the book
        book_data = scraper.scrape_book(url)

        # Save complete data
        scraper.save_to_json(book_data)

        # Save AI-optimized data for question generation
        scraper.save_for_ai_training(book_data)

    print("\n" + "=" * 60)
    print("Scraping complete! Check the 'zoho_learn_output' directory for results.")
    print("=" * 60)


if __name__ == "__main__":
    main()

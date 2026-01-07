"""
Job Posting Scraper
Extracts structured information from job posting URLs for AI consumption.
Supports both simple HTTP requests and Selenium for JavaScript-heavy sites.
"""

import requests
import json
import re
import time
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from datetime import datetime

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


class JobScraper:
    """
    A web scraper for extracting structured job posting information.
    Supports both simple HTTP requests and Selenium-based scraping.
    """

    def __init__(self, use_selenium: bool = False, headless: bool = True, user_agent: Optional[str] = None):
        """
        Initialize the JobScraper.

        Args:
            use_selenium: Use Selenium WebDriver for JavaScript-heavy sites
            headless: Run browser in headless mode (no GUI)
            user_agent: Custom user agent string. If None, uses default.
        """
        self.use_selenium = use_selenium
        self.headless = headless
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

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

        # Disable images and CSS for faster loading (optional)
        prefs = {
            'profile.managed_default_content_settings.images': 2,
        }
        chrome_options.add_experimental_option('prefs', prefs)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)

    def scrape(self, url: str, wait_time: int = 5) -> Dict[str, Any]:
        """
        Scrape a job posting URL and extract structured information.

        Args:
            url: The URL of the job posting to scrape
            wait_time: Time to wait for page to load (Selenium only)

        Returns:
            Dictionary containing structured job information
        """
        try:
            if self.use_selenium:
                soup = self._scrape_with_selenium(url, wait_time)
            else:
                soup = self._scrape_with_requests(url)

            # Detect site and use appropriate extractors
            if 'seek.com.au' in url:
                job_data = self._extract_seek_au(soup, url)
            else:
                job_data = self._extract_generic(soup, url)

            return job_data

        except Exception as e:
            return {
                'error': f'Error processing page: {str(e)}',
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

        # Get page source after JavaScript execution
        page_source = self.driver.page_source
        return BeautifulSoup(page_source, 'lxml')

    def _extract_seek_au(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract job information specifically for seek.com.au."""

        # Seek.com.au specific selectors
        job_data = {
            'url': url,
            'scraped_at': datetime.utcnow().isoformat(),
            'source': 'seek.com.au',
        }

        # Job title
        title_elem = soup.find('h1', {'data-automation': 'job-detail-title'})
        if not title_elem:
            title_elem = soup.find('h1')
        job_data['job_title'] = title_elem.get_text(strip=True) if title_elem else None

        # Company name
        company_elem = soup.find('span', {'data-automation': 'advertiser-name'})
        if not company_elem:
            company_elem = soup.find('a', {'data-automation': 'company-link'})
        job_data['company'] = company_elem.get_text(strip=True) if company_elem else None

        # Location
        location_elem = soup.find('span', {'data-automation': 'job-detail-location'})
        if not location_elem:
            location_elem = soup.find('a', {'data-automation': 'job-detail-location'})
        job_data['location'] = location_elem.get_text(strip=True) if location_elem else None

        # Salary
        salary_elem = soup.find('span', {'data-automation': 'job-detail-salary'})
        job_data['salary'] = salary_elem.get_text(strip=True) if salary_elem else None

        # Job type and work type
        work_type_elem = soup.find('span', {'data-automation': 'job-detail-work-type'})
        job_data['job_type'] = work_type_elem.get_text(strip=True) if work_type_elem else None

        # Job description
        desc_elem = soup.find('div', {'data-automation': 'jobAdDetails'})
        if not desc_elem:
            desc_elem = soup.find('div', class_=re.compile(r'job.*details|description', re.I))
        job_data['description'] = desc_elem.get_text(strip=True, separator=' ') if desc_elem else None

        # Extract structured information from description
        if desc_elem:
            job_data['requirements'] = self._extract_requirements(desc_elem)
            job_data['responsibilities'] = self._extract_responsibilities(desc_elem)
            job_data['benefits'] = self._extract_benefits(desc_elem)
            job_data['skills'] = self._extract_skills(desc_elem)
        else:
            job_data['requirements'] = None
            job_data['responsibilities'] = None
            job_data['benefits'] = None
            job_data['skills'] = None

        # Posted date
        posted_elem = soup.find('span', {'data-automation': 'job-detail-date'})
        if not posted_elem:
            posted_elem = soup.find('time')
        if posted_elem:
            if posted_elem.get('datetime'):
                job_data['posted_date'] = posted_elem['datetime']
            else:
                job_data['posted_date'] = posted_elem.get_text(strip=True)
        else:
            job_data['posted_date'] = None

        # Additional fields
        job_data['application_deadline'] = self._extract_deadline(soup)
        job_data['contact_info'] = self._extract_contact_info(soup)
        job_data['experience_level'] = self._extract_experience_level(soup)
        job_data['education'] = self._extract_education(soup)
        job_data['remote_option'] = self._detect_remote(soup)
        job_data['raw_text'] = self._extract_raw_text(soup)

        return job_data

    def _extract_generic(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract job information using generic selectors."""
        job_data = {
            'url': url,
            'scraped_at': datetime.utcnow().isoformat(),
            'job_title': self._extract_job_title(soup),
            'company': self._extract_company(soup),
            'location': self._extract_location(soup),
            'salary': self._extract_salary(soup),
            'job_type': self._extract_job_type(soup),
            'description': self._extract_description(soup),
            'requirements': self._extract_requirements(soup),
            'responsibilities': self._extract_responsibilities(soup),
            'benefits': self._extract_benefits(soup),
            'posted_date': self._extract_posted_date(soup),
            'application_deadline': self._extract_deadline(soup),
            'contact_info': self._extract_contact_info(soup),
            'skills': self._extract_skills(soup),
            'experience_level': self._extract_experience_level(soup),
            'education': self._extract_education(soup),
            'remote_option': self._detect_remote(soup),
            'raw_text': self._extract_raw_text(soup),
        }

        return job_data

    def _extract_job_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract job title from the page."""
        selectors = [
            ('h1', {'class': re.compile(r'job.*title', re.I)}),
            ('h1', {'class': re.compile(r'title', re.I)}),
            ('h1', {}),
            ('h2', {'class': re.compile(r'job.*title', re.I)}),
            ('meta', {'property': 'og:title'}),
            ('title', {}),
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

    def _extract_company(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract company name from the page."""
        selectors = [
            ('span', {'class': re.compile(r'company', re.I)}),
            ('div', {'class': re.compile(r'company', re.I)}),
            ('a', {'class': re.compile(r'company', re.I)}),
            ('meta', {'property': 'og:site_name'}),
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

    def _extract_location(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract job location from the page."""
        selectors = [
            ('span', {'class': re.compile(r'location', re.I)}),
            ('div', {'class': re.compile(r'location', re.I)}),
            ('p', {'class': re.compile(r'location', re.I)}),
        ]

        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)

        return None

    def _extract_salary(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract salary information from the page."""
        salary_pattern = re.compile(r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s*(?:per|/|\+)\s*(?:year|hour|month|annum))?', re.I)

        selectors = [
            ('span', {'class': re.compile(r'salary|compensation|pay', re.I)}),
            ('div', {'class': re.compile(r'salary|compensation|pay', re.I)}),
        ]

        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                text = element.get_text(strip=True)
                if text:
                    return text

        # Search entire page for salary pattern
        page_text = soup.get_text()
        match = salary_pattern.search(page_text)
        if match:
            return match.group(0)

        return None

    def _extract_job_type(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract job type (full-time, part-time, contract, etc.)."""
        job_types = ['full-time', 'part-time', 'contract', 'temporary', 'internship', 'freelance', 'casual', 'permanent']

        selectors = [
            ('span', {'class': re.compile(r'job.*type|employment.*type|work.*type', re.I)}),
            ('div', {'class': re.compile(r'job.*type|employment.*type|work.*type', re.I)}),
        ]

        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                text = element.get_text(strip=True).lower()
                for job_type in job_types:
                    if job_type in text:
                        return job_type.title()

        # Search page text
        page_text = soup.get_text().lower()
        for job_type in job_types:
            if job_type in page_text:
                return job_type.title()

        return None

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract job description from the page."""
        selectors = [
            ('div', {'class': re.compile(r'job.*description|description', re.I)}),
            ('section', {'class': re.compile(r'job.*description|description', re.I)}),
            ('div', {'id': re.compile(r'job.*description|description', re.I)}),
        ]

        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                return element.get_text(strip=True, separator=' ')

        return None

    def _extract_requirements(self, soup: BeautifulSoup) -> Optional[List[str]]:
        """Extract job requirements/qualifications."""
        requirements = []

        headers = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b', 'p'])
        for header in headers:
            header_text = header.get_text(strip=True).lower()
            if any(keyword in header_text for keyword in ['requirement', 'qualification', 'must have', 'essential', 'you will have', 'you\'ll have']):
                next_elem = header.find_next(['ul', 'ol', 'div', 'p'])
                if next_elem:
                    if next_elem.name in ['ul', 'ol']:
                        items = next_elem.find_all('li')
                        requirements.extend([item.get_text(strip=True) for item in items if item.get_text(strip=True)])
                    else:
                        text = next_elem.get_text(strip=True)
                        if text and text not in header_text:
                            requirements.append(text)

        return requirements if requirements else None

    def _extract_responsibilities(self, soup: BeautifulSoup) -> Optional[List[str]]:
        """Extract job responsibilities."""
        responsibilities = []

        headers = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b', 'p'])
        for header in headers:
            header_text = header.get_text(strip=True).lower()
            if any(keyword in header_text for keyword in ['responsibilit', 'duties', 'you will', 'role', 'day to day', 'what you\'ll do']):
                next_elem = header.find_next(['ul', 'ol', 'div', 'p'])
                if next_elem:
                    if next_elem.name in ['ul', 'ol']:
                        items = next_elem.find_all('li')
                        responsibilities.extend([item.get_text(strip=True) for item in items if item.get_text(strip=True)])
                    else:
                        text = next_elem.get_text(strip=True)
                        if text and text not in header_text:
                            responsibilities.append(text)

        return responsibilities if responsibilities else None

    def _extract_benefits(self, soup: BeautifulSoup) -> Optional[List[str]]:
        """Extract job benefits."""
        benefits = []

        headers = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b', 'p'])
        for header in headers:
            header_text = header.get_text(strip=True).lower()
            if any(keyword in header_text for keyword in ['benefit', 'perk', 'we offer', 'what we offer', 'why join']):
                next_elem = header.find_next(['ul', 'ol', 'div', 'p'])
                if next_elem:
                    if next_elem.name in ['ul', 'ol']:
                        items = next_elem.find_all('li')
                        benefits.extend([item.get_text(strip=True) for item in items if item.get_text(strip=True)])
                    else:
                        text = next_elem.get_text(strip=True)
                        if text and text not in header_text:
                            benefits.append(text)

        return benefits if benefits else None

    def _extract_posted_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract job posting date."""
        selectors = [
            ('time', {}),
            ('span', {'class': re.compile(r'date|posted', re.I)}),
            ('div', {'class': re.compile(r'date|posted', re.I)}),
        ]

        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                if tag == 'time' and element.get('datetime'):
                    return element['datetime']
                text = element.get_text(strip=True)
                if text:
                    return text

        return None

    def _extract_deadline(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract application deadline."""
        page_text = soup.get_text()
        deadline_pattern = re.compile(r'(?:deadline|apply by|closes on)[:\s]+([^\n]+)', re.I)
        match = deadline_pattern.search(page_text)
        if match:
            return match.group(1).strip()

        return None

    def _extract_contact_info(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """Extract contact information."""
        contact = {}

        # Extract email
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        emails = email_pattern.findall(soup.get_text())
        if emails:
            contact['email'] = emails[0]

        # Extract phone (Australian format)
        phone_pattern = re.compile(r'\b(?:\+?61|0)[2-478](?:[ -]?[0-9]){8}\b')
        phones = phone_pattern.findall(soup.get_text())
        if phones:
            contact['phone'] = phones[0]

        return contact if contact else None

    def _extract_skills(self, soup: BeautifulSoup) -> Optional[List[str]]:
        """Extract required skills."""
        skills = []

        headers = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b', 'p'])
        for header in headers:
            header_text = header.get_text(strip=True).lower()
            if any(keyword in header_text for keyword in ['skill', 'technical', 'competenc', 'experience with']):
                next_elem = header.find_next(['ul', 'ol', 'div', 'p'])
                if next_elem:
                    if next_elem.name in ['ul', 'ol']:
                        items = next_elem.find_all('li')
                        skills.extend([item.get_text(strip=True) for item in items if item.get_text(strip=True)])
                    else:
                        text = next_elem.get_text(strip=True)
                        if text and text not in header_text:
                            skills.append(text)

        return skills if skills else None

    def _extract_experience_level(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract experience level required."""
        experience_keywords = {
            'entry level': r'\b(?:entry[- ]level|junior|graduate|0-2 years|early career)\b',
            'mid level': r'\b(?:mid[- ]level|intermediate|2-5 years)\b',
            'senior level': r'\b(?:senior|lead|5\+ years|experienced)\b',
            'executive': r'\b(?:executive|director|c-level|vp)\b',
        }

        page_text = soup.get_text().lower()
        for level, pattern in experience_keywords.items():
            if re.search(pattern, page_text, re.I):
                return level.title()

        return None

    def _extract_education(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract education requirements."""
        education_pattern = re.compile(
            r'\b(?:bachelor|master|phd|mba|associate|diploma|degree)(?:\'s)?\s+(?:degree|in|of)?\s+[^\n.]+',
            re.I
        )

        page_text = soup.get_text()
        match = education_pattern.search(page_text)
        if match:
            return match.group(0).strip()

        return None

    def _detect_remote(self, soup: BeautifulSoup) -> bool:
        """Detect if the job offers remote work option."""
        remote_keywords = ['remote', 'work from home', 'wfh', 'telecommute', 'virtual', 'hybrid', 'flexible location']
        page_text = soup.get_text().lower()

        return any(keyword in page_text for keyword in remote_keywords)

    def _extract_raw_text(self, soup: BeautifulSoup) -> str:
        """Extract all readable text from the page for fallback analysis."""
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()

        text = soup.get_text(separator=' ', strip=True)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        return text

    def save_to_json(self, job_data: Dict[str, Any], output_file: str):
        """
        Save scraped job data to a JSON file.

        Args:
            job_data: The scraped job data dictionary
            output_file: Path to the output JSON file
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(job_data, f, indent=2, ensure_ascii=False)

    def save_multiple_to_json(self, jobs_data: List[Dict[str, Any]], output_file: str):
        """
        Save multiple scraped job postings to a JSON file.

        Args:
            jobs_data: List of scraped job data dictionaries
            output_file: Path to the output JSON file
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False)

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

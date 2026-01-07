# Web Scraper Collection

A Python-based collection of web scrapers that extract structured information from various sources and formats it for AI consumption and automation.

**Includes:**
- **Job Posting Scraper** - Extract job information from job boards (seek.com.au, Indeed, etc.)
- **Zoho Learn Scraper** - Extract educational content for AI-powered question generation and spaced repetition learning

**Now with Selenium support** for JavaScript-heavy sites!

## Features

- **Dual scraping modes:**
  - Simple HTTP requests (fast, for static sites)
  - Selenium WebDriver (for JavaScript-heavy sites)

- **Extracts comprehensive job information:**
  - Job title and company name
  - Location and remote work options
  - Salary information
  - Job type (full-time, part-time, contract, etc.)
  - Job description and responsibilities
  - Requirements and qualifications
  - Required skills
  - Benefits
  - Education requirements
  - Experience level
  - Contact information
  - Posted date and application deadline

- **Site-specific optimizations:**
  - seek.com.au (Australian job board)
  - Generic fallback for other sites

- **AI-friendly output:**
  - Clean JSON format
  - Structured data with consistent naming
  - Raw text fallback for unstructured analysis

- Handles errors gracefully
- Supports batch scraping of multiple job postings
- Context manager support for automatic cleanup

## Project Files

### Job Scraping Tools
- **`scraper_gui.py`** - 🖥️ Single job scraper GUI - paste one URL, get instant results
- **`batch_scraper_gui.py`** - 🚀 Batch scraper GUI - paste multiple URLs, get individual JSON files
- **`cv_customizer_gui.py`** - 🤖 CV Customizer with Claude AI - generate tailored CVs for each job
- **`job_scraper.py`** - Core scraping engine with Selenium support
- **`example.py`** - Python code examples for programmatic use

### Educational Content Scraping Tools
- **`zoho_learn_scraper_gui.py`** - 📚 Zoho Learn scraper GUI - extract educational content for AI learning
- **`zoho_learn_scraper.py`** - Educational content scraper with chapter/article navigation
- **`zoho_learn_example.py`** - Usage examples and integration patterns
- **`ZOHO_LEARN_SCRAPER_README.md`** - Detailed documentation for Zoho Learn scraper

### Shared Files
- **`prompts/`** - 📝 Customizable AI prompt templates (CV styles, cover letters, talking points)
- **`requirements.txt`** - Python package dependencies
- **`README.md`** - This documentation file

**Complete Workflow:**
1. **Scrape jobs:** Run `batch_scraper_gui.py` → Get folder with JSON files
2. **Customize CVs:** Run `cv_customizer_gui.py` → Select template style → Get tailored CVs for each job
3. **Polish:** Copy plain text into Canva/Resume.io for beautiful formatting
4. **Refine:** Edit templates in `prompts/` folder to improve future outputs

## Installation

### 1. Clone this repository

### 2. Install required dependencies:

```bash
pip install -r requirements.txt
```

This will install:
- `requests` - For HTTP requests
- `beautifulsoup4` - For HTML parsing
- `lxml` - Fast XML/HTML parser
- `selenium` - For browser automation
- `webdriver-manager` - Automatic ChromeDriver management

### 3. Chrome browser

Selenium requires Chrome browser to be installed on your system. The ChromeDriver will be automatically downloaded and managed by `webdriver-manager`.

## Usage

### ⭐ GUI Application (EASIEST - Recommended for Beginners)

The easiest way to use the scraper is with the graphical interface:

```bash
python scraper_gui.py
```

This opens a window where you can:
1. **Paste any job URL** (seek.com.au, Indeed, LinkedIn, etc.)
2. **Configure options** (Selenium on/off, headless mode, wait time)
3. **Click "Scrape Job Posting"** and see results instantly
4. **Save to JSON** with one click

**No coding required!** Perfect for:
- Quick one-off job scraping
- Testing different URLs
- Viewing results immediately
- Non-programmers who want to use the tool

![GUI Preview: Simple window with URL input, options, and results display]

---

### ⭐⭐ Batch Scraper GUI (For Multiple Jobs - RECOMMENDED for CV Customization)

The batch scraper lets you scrape multiple jobs at once and saves each to a separate JSON file:

```bash
python batch_scraper_gui.py
```

This opens a window where you can:
1. **Paste multiple job URLs** (one per line) - paste 10, 20, or even 50 URLs
2. **Configure options** (same as single scraper)
3. **Click "Start Batch Scraping"** and watch the progress
4. **Get organized output** - creates timestamped folder with individual JSON files

**Perfect for:**
- Job application campaigns (applying to multiple jobs)
- Building a job database
- CV customization workflow (scrape → analyze → customize)
- Comparing multiple job opportunities

**Output structure:**
```
batches/
└── batch_2025-11-07_143052/
    ├── job_001_senior_python_developer_techcorp.json
    ├── job_002_backend_engineer_startup.json
    ├── job_003_fullstack_developer_bigcompany.json
    └── ... (one JSON file per job)
```

**Features:**
- Real-time progress tracking (Job 3 of 10...)
- Success/error logging for each job
- Auto-generated filenames based on job title + company
- One-click "Open Folder" button to view results
- Can load URLs from a text file
- Can stop scraping mid-batch if needed

---

### ⭐⭐⭐ CV Customizer with Claude AI (The Final Step!)

After scraping jobs, use AI to generate customized CVs for each position:

```bash
python cv_customizer_gui.py
```

This powerful tool:
1. **Loads multiple documents about YOU** - upload your resume, LinkedIn profile, portfolio, cover letters, etc. (PDF, DOCX, HTML, TXT)
2. **Claude AI reads everything** - builds a complete understanding of your background
3. **Analyzes each job** - understands what each employer wants
4. **Generates customized content** - tailors your CV, cover letter, and talking points for EACH job

**Perfect for:**
- Job application campaigns (apply to 10-20 jobs efficiently)
- Maximizing interview chances (show exactly what each employer wants)
- Saving time (no manual rewriting)
- Maintaining consistency (AI ensures quality)

**Setup Requirements:**
1. **Get Claude API key**: Visit https://console.anthropic.com/
   - Sign up for Anthropic account
   - Add payment method (pay-as-you-go)
   - Create API key
   - Cost: ~$0.015 per 1M tokens (very cheap!)

2. **Install dependencies**:
```bash
pip install anthropic pypdf python-docx
```

**How to Use:**

**Step 1: Upload Your Documents**
- Click "Add Documents"
- Select ALL documents that describe you:
  - Your master resume/CV (PDF or DOCX)
  - LinkedIn profile (save as PDF or HTML)
  - Portfolio website (save as HTML)
  - Past cover letters
  - Project descriptions
  - Anything that shows your skills/experience
- The more context, the better the AI customization!

**Step 2: Select Job Folder**
- Click "Browse" next to "Job Postings"
- Select the batch folder from `batch_scraper_gui.py`
- All JSON files will load automatically

**Step 3: Choose Your Templates** 🎨
- **CV Style**: Select from multiple professional templates:
  - **Professional (Corporate/Finance)** - Formal tone, quantifiable achievements, business impact
  - **Technical (Software/Engineering)** - Tech-focused, project-heavy, specific technologies
  - **Creative (Design/Marketing)** - Show personality, portfolio-focused, narrative style
- **Cover Letter**: Choose your tone:
  - **Formal (Corporate)** - Traditional business letter format
  - **Casual (Startup/Tech)** - Conversational and warm tone
- **Edit Templates**: Click "✏️ Edit Template" to customize prompts in your text editor
  - Templates are stored in `prompts/` folder as `.txt` files
  - Modify formatting, tone, sections, or instructions
  - Changes take effect immediately on next generation

**Step 4: Configure API**
- Paste your Claude API key
- Click "Test API Key" to verify
- Choose what to generate:
  - ✅ Customized CV (highly recommended)
  - ✅ Cover Letter (recommended)
  - ☐ Interview Talking Points (optional)
- Select Claude model (default: claude-3-5-sonnet is best)

**Step 5: Generate!**
- Click "Generate Customized CVs"
- Watch the progress
- Get output folder with files like:
  - `job_001_senior_python_CV.txt`
  - `job_001_senior_python_CoverLetter.txt`
  - `job_002_backend_engineer_CV.txt`
  - etc.

**Output Format:**
Plain text files - perfect for:
- Copy/paste into Canva for beautiful design
- Import into Resume.io or similar tools
- Paste into Google Docs for formatting
- Quick edits before final polish

**Example Output:**
```
customized_cvs/
└── batch_2025-11-07_150000/
    ├── job_001_senior_python_techcorp_CV.txt
    ├── job_001_senior_python_techcorp_CoverLetter.txt
    ├── job_002_backend_engineer_startup_CV.txt
    ├── job_002_backend_engineer_startup_CoverLetter.txt
    └── ...
```

**What Claude AI Does:**
- Analyzes job requirements deeply
- Identifies matching skills from your profile
- Rewrites experience to highlight relevant points
- Uses keywords from job posting (ATS-friendly)
- Adjusts tone for company culture
- Creates compelling narratives
- Maintains honesty (doesn't fabricate)

**Tips for Best Results:**
1. Upload comprehensive documents (more info = better customization)
2. Include variety: resume + LinkedIn + portfolio gives complete picture
3. Keep documents current and accurate
4. **Customize templates** to match your personal style and target industry
5. Review AI output before final submission (always!)
6. Use Claude Sonnet 3.5 for best quality

**Customizable Template System:**

All AI prompts are stored as editable text files in the `prompts/` directory:
- `cv_professional.txt` - Professional/corporate CV style
- `cv_technical.txt` - Technical/engineering CV style
- `cv_creative.txt` - Creative/design CV style
- `cover_letter_formal.txt` - Formal corporate cover letter
- `cover_letter_casual.txt` - Casual startup/tech cover letter
- `talking_points.txt` - Interview preparation and talking points

You can customize these templates to:
- Adjust tone and language style
- Modify section headers and formatting
- Add or remove sections
- Include industry-specific requirements
- Change output structure

Simply click "✏️ Edit Template" in the GUI or open the files directly in any text editor. Your changes will be used for all future CV generations!

---

## Zoho Learn Educational Content Scraper

Extract comprehensive educational content from Zoho Learn shared links for AI-powered question generation and spaced repetition learning.

### 🎯 Use Cases

- **AI-Powered Question Generation**: Extract content to automatically generate learning questions
- **Spaced Repetition Learning**: Create flashcard systems with optimal review intervals (like Anki, SuperMemo)
- **Educational AI Assistants**: Build Coursera-style AI tutors that discuss content with learners
- **Content Backup**: Archive educational materials with images for offline access
- **Custom Learning Apps**: Build educational applications using structured content

### 🚀 Quick Start

#### GUI Application (Recommended)

```bash
python zoho_learn_scraper_gui.py
```

Features:
1. Paste any Zoho Learn shared book URL
2. Automatically extracts all chapters and articles
3. Downloads images with proper context
4. Generates two JSON formats:
   - Complete data with full structure
   - AI-ready format optimized for question generation
5. Includes spaced repetition metadata (SM-2 algorithm inspired)

#### Command Line

```bash
python zoho_learn_scraper.py "https://learn.zoho.com/portal/yourorg/shared/book123"
```

#### Python Script

```python
from zoho_learn_scraper import ZohoLearnScraper

with ZohoLearnScraper(use_selenium=True) as scraper:
    book_data = scraper.scrape_book("https://learn.zoho.com/...")
    scraper.save_to_json(book_data)
    scraper.save_for_ai_training(book_data)
```

### 📦 Output Structure

The scraper generates:

1. **Complete JSON** - Full structure with metadata
2. **AI-Ready JSON** - Optimized for question generation
3. **Images Folder** - All images downloaded locally

```
zoho_learn_output/
├── Book_Title_20260106_120000.json          # Complete data
├── Book_Title_ai_ready_20260106_120000.json # AI-ready format
└── images/
    ├── ch1_art1_img1.png
    ├── ch1_art2_img1.jpg
    └── ...
```

### 🤖 AI Question Generation Integration

Example workflow:

```python
# 1. Scrape educational content
with ZohoLearnScraper() as scraper:
    book_data = scraper.scrape_book("https://learn.zoho.com/...")
    ai_path = scraper.save_for_ai_training(book_data)

# 2. Load AI-ready data
with open(ai_path, 'r') as f:
    learning_data = json.load(f)

# 3. Generate questions for each learning unit
for unit in learning_data['learning_units']:
    # Send to Claude/GPT to generate questions
    questions = generate_questions(
        content=unit['content'],
        difficulty=unit['metadata']['difficulty']
    )

    # Use spaced repetition intervals
    schedule_reviews(questions, unit['metadata']['spaced_repetition_intervals'])
```

### 📚 Spaced Repetition Support

Includes metadata for optimal learning retention:
- **Suggested Intervals**: [1, 3, 7, 14, 30, 60, 120] days
- **Difficulty Estimation**: Easy/Medium/Hard based on content length
- **Context Preservation**: Maintains chapter hierarchy for learning flow

### 📖 Features

- ✅ Complete book structure extraction (chapters → articles)
- ✅ Structured content preservation (headings, paragraphs, lists, code, tables)
- ✅ Image downloading with captions and context
- ✅ AI-optimized output format
- ✅ Spaced repetition metadata (SM-2 inspired)
- ✅ Progress tracking and error handling
- ✅ Word count and reading time estimates
- ✅ Context preservation for AI understanding

### 📄 Full Documentation

See **`ZOHO_LEARN_SCRAPER_README.md`** for:
- Detailed API documentation
- Integration examples
- Spaced repetition implementation
- AI question generation patterns
- Troubleshooting guide
- Advanced configuration options

---

### Quick Start - Selenium Mode (Recommended for seek.com.au)

```python
from job_scraper import JobScraper

# Initialize with Selenium enabled
scraper = JobScraper(use_selenium=True, headless=True)

# Scrape a seek.com.au job posting
job_data = scraper.scrape("https://www.seek.com.au/job/88185524")

# Save to JSON file
scraper.save_to_json(job_data, "job.json")

# Clean up
scraper.close()
```

### Basic Usage - Simple HTTP Mode

```python
from job_scraper import JobScraper

# Initialize without Selenium (faster but may not work for JS-heavy sites)
scraper = JobScraper(use_selenium=False)

# Scrape a job posting
job_data = scraper.scrape("https://example.com/job-posting")

# Save to JSON file
scraper.save_to_json(job_data, "output.json")
```

### Using the Example Script

The included `example.py` shows three different usage patterns:

```bash
python example.py
```

By default, it will scrape the seek.com.au URL you provided. Edit the file to:
- Enable/disable different examples
- Add your own job URLs
- Adjust scraping parameters

### Context Manager (Recommended)

Use the context manager for automatic cleanup:

```python
from job_scraper import JobScraper

# Browser automatically closes when done
with JobScraper(use_selenium=True, headless=True) as scraper:
    job_data = scraper.scrape("https://www.seek.com.au/job/88185524")
    scraper.save_to_json(job_data, "job.json")
```

### Batch Scraping Multiple Jobs

```python
from job_scraper import JobScraper

job_urls = [
    "https://www.seek.com.au/job/88185524",
    "https://www.seek.com.au/job/88185525",
    "https://www.seek.com.au/job/88185526"
]

with JobScraper(use_selenium=True, headless=True) as scraper:
    all_jobs = []
    for url in job_urls:
        job_data = scraper.scrape(url, wait_time=5)
        all_jobs.append(job_data)

    # Save all jobs to one file
    scraper.save_multiple_to_json(all_jobs, "all_jobs.json")
```

### Advanced Options

```python
from job_scraper import JobScraper

# Customize scraper behavior
scraper = JobScraper(
    use_selenium=True,           # Enable Selenium
    headless=False,              # Show browser window (useful for debugging)
    user_agent="Custom Agent"    # Custom user agent string
)

# Adjust wait time for slower sites
job_data = scraper.scrape(url, wait_time=10)
```

## Configuration Options

### JobScraper Parameters

- `use_selenium` (bool, default: False)
  - `False`: Use simple HTTP requests (fast)
  - `True`: Use Selenium WebDriver (for JavaScript sites)

- `headless` (bool, default: True)
  - `True`: Run browser in background (no GUI)
  - `False`: Show browser window (useful for debugging)

- `user_agent` (str, optional)
  - Custom user agent string
  - Default: Chrome on Windows

### scrape() Parameters

- `url` (str, required)
  - The job posting URL to scrape

- `wait_time` (int, default: 5)
  - Seconds to wait for page to load (Selenium only)
  - Increase for slower sites or slow connections

## Output Format

The scraper returns data in the following JSON structure:

```json
{
  "url": "https://www.seek.com.au/job/88185524",
  "scraped_at": "2025-11-07T01:34:00.000000",
  "source": "seek.com.au",
  "job_title": "Software Engineer",
  "company": "Example Company",
  "location": "Sydney NSW",
  "salary": "$120,000 - $150,000 per year",
  "job_type": "Full-Time",
  "description": "Full job description text...",
  "requirements": [
    "Bachelor's degree in Computer Science",
    "5+ years of experience",
    "Proficiency in Python"
  ],
  "responsibilities": [
    "Design and implement features",
    "Collaborate with team members"
  ],
  "benefits": [
    "Competitive salary package",
    "Flexible work arrangements",
    "Professional development opportunities"
  ],
  "posted_date": "2025-11-01",
  "application_deadline": null,
  "contact_info": {
    "email": "jobs@example.com",
    "phone": "02 1234 5678"
  },
  "skills": [
    "Python",
    "JavaScript",
    "React",
    "AWS"
  ],
  "experience_level": "Senior Level",
  "education": "Bachelor's degree in Computer Science or related field",
  "remote_option": true,
  "raw_text": "Complete page text for fallback analysis..."
}
```

## Supported Sites

### Optimized For:
- **seek.com.au** - Australia's #1 job board (uses site-specific selectors)

### Generic Support:
- Most other job boards using standard HTML patterns
- Sites with minimal JavaScript

### May Require Adjustments:
- LinkedIn (requires login)
- Indeed (heavy JavaScript, use Selenium)
- Glassdoor (anti-scraping measures)

## AI-Friendly Output

The structured JSON output is designed to be easily processed by AI systems:

- **Clear field names**: All fields use descriptive, consistent naming
- **Structured data**: Information is organized into logical categories
- **Lists for multiple items**: Requirements, skills, and benefits are in array format
- **Raw text fallback**: Complete page text is included for AI models that can analyze unstructured data
- **Metadata**: Includes URL, source, and scrape timestamp for tracking

Perfect for feeding into:
- GPT models for job analysis
- Automated job matching systems
- Resume tailoring tools
- Job market analysis pipelines

## Error Handling

If scraping fails, the output will include an error field:

```json
{
  "error": "Error processing page: <details>",
  "url": "https://example.com/job-posting",
  "scraped_at": "2025-11-07T01:34:00.000000"
}
```

Common errors and solutions:

| Error | Solution |
|-------|----------|
| "Failed to fetch URL" | Check internet connection, URL validity |
| "No such element" | Page structure changed, may need selector updates |
| "Timeout" | Increase `wait_time` parameter |
| "ChromeDriver" issues | Ensure Chrome browser is installed |

## Best Practices

1. **Use Selenium for JavaScript sites**
   - seek.com.au, Indeed, LinkedIn need Selenium
   - Simple static sites can use HTTP mode

2. **Respect rate limits**
   - Add delays between requests
   - Don't overwhelm servers

3. **Check robots.txt**
   - Respect website scraping policies
   - Some sites prohibit automated access

4. **Handle errors gracefully**
   - Always check for 'error' key in results
   - Log failures for debugging

5. **Use context managers**
   - Ensures proper cleanup of browser resources

## Troubleshooting

### "Selenium not installed" error
```bash
pip install selenium webdriver-manager
```

### Chrome/ChromeDriver issues
- Ensure Chrome browser is installed
- The ChromeDriver is auto-managed by webdriver-manager

### Page loads but no data extracted
- Try increasing `wait_time`
- Set `headless=False` to visually debug
- Check if site requires login

### Memory issues with batch scraping
- Close scraper periodically: `scraper.close()`
- Process in smaller batches
- Use context manager for automatic cleanup

## Limitations

- Some sites use anti-scraping measures (CAPTCHAs, rate limiting)
- Login-required sites need additional authentication handling
- Dynamic content may require longer wait times
- Selenium adds overhead (slower than simple HTTP)

## Future Enhancements

### Job Scraper
- ✅ ~~Selenium support~~ (DONE!)
- ✅ ~~Site-specific extractors~~ (seek.com.au done!)
- ✅ ~~Graphical user interface~~ (DONE!)
- ✅ ~~Batch URL scraping in GUI~~ (DONE!)
- ✅ ~~CV/Resume customization with Claude API~~ (DONE!)
- ✅ ~~Multi-document profile loading (PDF, DOCX, HTML)~~ (DONE!)
- ✅ ~~Customizable AI prompt templates~~ (DONE!)
- Auto-save API key (encrypted storage)
- Rate limiting and retry logic
- Proxy support
- More site-specific extractors (LinkedIn, Indeed, Glassdoor)
- Database storage option
- API endpoint wrapper
- Command-line interface
- CAPTCHA handling

### Zoho Learn Scraper
- ✅ ~~Educational content extraction~~ (DONE!)
- ✅ ~~Chapter and article navigation~~ (DONE!)
- ✅ ~~Image downloading~~ (DONE!)
- ✅ ~~Spaced repetition metadata~~ (DONE!)
- ✅ ~~AI-ready output format~~ (DONE!)
- Built-in AI question generation
- Direct Anki/SuperMemo integration
- Video content extraction
- Audio transcription
- Multi-language support
- Progress tracking dashboard
- Interactive learning mode

## License

This project is provided as-is for educational and personal use.

## Contributing

Feel free to submit issues or pull requests for improvements.

## Acknowledgments

- Uses Selenium for browser automation
- BeautifulSoup for HTML parsing
- webdriver-manager for driver management

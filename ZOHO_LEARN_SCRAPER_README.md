# Zoho Learn Educational Content Scraper

A comprehensive tool for extracting educational content from Zoho Learn shared links, designed to prepare content for AI-powered question generation and spaced repetition learning systems.

## Features

- **Complete Book Extraction**: Scrapes entire Zoho Learn books including all chapters and articles
- **Structured Content Preservation**: Maintains hierarchy and context (headings, paragraphs, lists, code blocks, tables)
- **Image Downloading**: Automatically downloads and saves all images with proper context
- **AI-Ready Output**: Generates optimized JSON format for AI question generation
- **Spaced Repetition Support**: Includes metadata for spaced repetition learning (SM-2 algorithm inspired)
- **GUI & CLI**: Both graphical interface and command-line usage
- **Progress Tracking**: Real-time progress updates during scraping

## Use Cases

1. **AI-Powered Question Generation**: Extract content to generate learning questions automatically
2. **Spaced Repetition Learning**: Create flashcard systems with optimal review intervals
3. **Content Backup**: Archive educational materials for offline access
4. **Learning Analytics**: Analyze content structure and difficulty
5. **Custom Learning Apps**: Build educational applications using scraped content

## Installation

### Prerequisites

```bash
pip install -r requirements.txt
```

Required packages:
- `requests>=2.31.0`
- `beautifulsoup4>=4.12.0`
- `lxml>=4.9.0`
- `selenium>=4.15.0`
- `webdriver-manager>=4.0.1`

## Usage

### Option 1: Graphical User Interface (Recommended for Beginners)

```bash
python zoho_learn_scraper_gui.py
```

Features:
- Easy-to-use interface
- Visual progress tracking
- One-click scraping and saving
- Built-in data preview

### Option 2: Command Line

```bash
python zoho_learn_scraper.py "https://learn.zoho.com/portal/yourorg/shared/book123"
```

### Option 3: Python Script

```python
from zoho_learn_scraper import ZohoLearnScraper

# Create scraper instance
with ZohoLearnScraper(use_selenium=True, headless=True) as scraper:
    # Scrape the book
    book_data = scraper.scrape_book("https://learn.zoho.com/portal/...")

    # Save complete data
    scraper.save_to_json(book_data)

    # Save AI-optimized data
    scraper.save_for_ai_training(book_data)
```

## Output Structure

### Complete JSON Output

The scraper generates two types of JSON files:

#### 1. Complete Data (`book_title_YYYYMMDD_HHMMSS.json`)

Full structure with all metadata:

```json
{
  "url": "https://learn.zoho.com/...",
  "title": "Book Title",
  "description": "Book description",
  "scraped_at": "2026-01-06T12:00:00",
  "chapters": [
    {
      "chapter_number": 1,
      "title": "Chapter Title",
      "articles": [
        {
          "article_number": 1,
          "title": "Article Title",
          "url": "https://...",
          "content": {
            "structured": [
              {
                "type": "heading",
                "level": 2,
                "text": "Section Title"
              },
              {
                "type": "paragraph",
                "text": "Content text..."
              },
              {
                "type": "list",
                "list_type": "unordered",
                "items": ["Item 1", "Item 2"]
              }
            ],
            "images": [
              {
                "url": "https://...",
                "local_path": "zoho_learn_output/images/ch1_art1_img1.png",
                "alt_text": "Description",
                "caption": "Image caption"
              }
            ],
            "raw_text": "Full article text..."
          },
          "metadata": {
            "chapter_number": 1,
            "word_count": 500,
            "estimated_reading_time_minutes": 3,
            "spaced_repetition_metadata": {
              "initial_interval_days": 1,
              "suggested_intervals": [1, 3, 7, 14, 30, 60, 120],
              "difficulty_estimate": "medium",
              "content_type": "educational_article"
            }
          }
        }
      ]
    }
  ],
  "metadata": {
    "total_chapters": 5,
    "total_articles": 25,
    "total_images": 50,
    "scraper_version": "1.0",
    "spaced_repetition_ready": true
  }
}
```

#### 2. AI-Ready Data (`book_title_ai_ready_YYYYMMDD_HHMMSS.json`)

Optimized for AI question generation:

```json
{
  "book_title": "Book Title",
  "learning_units": [
    {
      "id": "ch1_art1",
      "chapter": "Chapter Title",
      "chapter_number": 1,
      "title": "Article Title",
      "content": "Formatted content with headings, paragraphs, lists...",
      "structured_content": [...],
      "images": [...],
      "metadata": {
        "word_count": 500,
        "estimated_reading_time_minutes": 3,
        "difficulty": "medium",
        "spaced_repetition_intervals": [1, 3, 7, 14, 30, 60, 120]
      },
      "context": {
        "previous_chapter": "Previous Chapter",
        "source_url": "https://..."
      }
    }
  ],
  "summary": {
    "total_learning_units": 25,
    "total_chapters": 5,
    "total_images": 50,
    "total_words": 12500,
    "estimated_total_reading_time_minutes": 63
  }
}
```

### Directory Structure

```
zoho_learn_output/
├── Book_Title_20260106_120000.json          # Complete data
├── Book_Title_ai_ready_20260106_120000.json # AI-ready data
└── images/
    ├── ch1_art1_img1.png
    ├── ch1_art1_img2.jpg
    ├── ch1_art2_img1.png
    └── ...
```

## Spaced Repetition Learning

The scraper includes metadata designed for spaced repetition systems (like Anki, SuperMemo):

### Suggested Intervals (SM-2 Inspired)

- **Day 1**: Initial review
- **Day 3**: Second review
- **Day 7**: First week review
- **Day 14**: Two-week review
- **Day 30**: One-month review
- **Day 60**: Two-month review
- **Day 120**: Long-term retention check

### Difficulty Estimation

Based on content analysis:
- **Easy**: < 300 words
- **Medium**: 300-1000 words
- **Hard**: > 1000 words

## Integration with AI Question Generation

### Example: Using with Claude/GPT for Question Generation

```python
import json
from zoho_learn_scraper import ZohoLearnScraper

# 1. Scrape the content
with ZohoLearnScraper() as scraper:
    book_data = scraper.scrape_book("https://learn.zoho.com/...")
    ai_ready_path = scraper.save_for_ai_training(book_data)

# 2. Load AI-ready data
with open(ai_ready_path, 'r') as f:
    learning_data = json.load(f)

# 3. Generate questions for each learning unit
for unit in learning_data['learning_units']:
    prompt = f"""
    Based on this educational content, generate 5 multiple-choice questions:

    Title: {unit['title']}
    Content: {unit['content']}

    For each question:
    - Create 4 answer options (1 correct, 3 incorrect)
    - Explain why the correct answer is right
    - Reference the specific part of the content
    """

    # Send to AI (Claude, GPT, etc.)
    # questions = ai_generate(prompt)
    # Store questions with spaced repetition metadata
```

### Example: Question Format

```json
{
  "learning_unit_id": "ch1_art1",
  "questions": [
    {
      "question": "What is the main purpose of X?",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "B",
      "explanation": "According to the content...",
      "difficulty": "medium",
      "spaced_repetition": {
        "next_review_day": 1,
        "review_count": 0
      }
    }
  ]
}
```

## Advanced Options

### Custom Output Directory

```python
scraper = ZohoLearnScraper(output_dir="my_custom_directory")
```

### Disable Selenium (for simple HTML sites)

```python
scraper = ZohoLearnScraper(use_selenium=False)
```

### Adjust Wait Time

```python
book_data = scraper.scrape_book(url, wait_time=10)  # Wait 10 seconds per page
```

### Custom User Agent

```python
scraper = ZohoLearnScraper(user_agent="My Custom User Agent")
```

## Troubleshooting

### "Selenium not installed" Error

```bash
pip install selenium webdriver-manager
```

### Images Not Downloading

- Check internet connection
- Verify image URLs are accessible
- Some images may be protected or require authentication

### Empty Content

- Increase wait time (some pages load slowly)
- Try with `use_selenium=True`
- Check if the URL is publicly accessible

### Rate Limiting

- Add delays between requests (built-in 1 second delay)
- Use `wait_time` parameter to increase delays
- Be respectful to the server

## Best Practices

1. **Test First**: Start with a small book to test the scraper
2. **Check Permissions**: Ensure you have permission to scrape the content
3. **Backup Data**: Keep backups of scraped content
4. **Review Output**: Always review the scraped data for accuracy
5. **Attribution**: Maintain source URLs and give credit to original authors

## Use with AI Learning Systems

### Creating a Spaced Repetition App

1. **Scrape Content**: Use this tool to extract learning materials
2. **Generate Questions**: Use AI (Claude, GPT) to create questions from content
3. **Implement Scheduling**: Use the suggested intervals for review scheduling
4. **Track Progress**: Monitor user performance and adjust intervals
5. **Provide Context**: Use images and structured content for rich learning experience

### Integration Example (Coursera-style)

```python
# Pseudocode for AI-powered learning system
class LearningSession:
    def __init__(self, learning_unit):
        self.unit = learning_unit
        self.questions = generate_questions(learning_unit['content'])
        self.ai_tutor = AITutor()

    def start_session(self):
        for question in self.questions:
            # Show question
            user_answer = get_user_input()

            # Check answer
            is_correct = check_answer(user_answer, question['correct_answer'])

            # AI provides contextual help
            if not is_correct:
                explanation = self.ai_tutor.explain(
                    question=question,
                    user_answer=user_answer,
                    context=self.unit['content']
                )
                show_explanation(explanation)

            # Update spaced repetition schedule
            update_schedule(question, is_correct)
```

## Future Enhancements

- [ ] Support for video content extraction
- [ ] Audio transcription for embedded media
- [ ] Multi-language support
- [ ] Direct integration with Anki/SuperMemo
- [ ] Built-in question generation
- [ ] Progress tracking dashboard
- [ ] Collaborative learning features

## License

This tool is for educational purposes. Always respect copyright and terms of service of the content you scrape.

## Support

For issues, questions, or contributions, please refer to the main repository README.

---

**Happy Learning! 📚**

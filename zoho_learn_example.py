"""
Example usage of the Zoho Learn Scraper
Demonstrates various ways to use the scraper and process the data
"""

from zoho_learn_scraper import ZohoLearnScraper
import json


def example_basic_scrape():
    """Basic scraping example"""
    print("Example 1: Basic Scraping")
    print("=" * 60)

    # Replace with your actual Zoho Learn URL
    url = "https://learn.zoho.com/portal/yourorg/shared/book123"

    with ZohoLearnScraper(use_selenium=True, headless=True) as scraper:
        # Scrape the book
        book_data = scraper.scrape_book(url)

        # Save to JSON
        scraper.save_to_json(book_data)

        # Save AI-ready format
        scraper.save_for_ai_training(book_data)

    print("\n✓ Scraping complete!")


def example_custom_output():
    """Example with custom output directory"""
    print("\nExample 2: Custom Output Directory")
    print("=" * 60)

    url = "https://learn.zoho.com/portal/yourorg/shared/book123"

    with ZohoLearnScraper(
        use_selenium=True,
        headless=True,
        output_dir="my_learning_content"
    ) as scraper:
        book_data = scraper.scrape_book(url, wait_time=7)
        scraper.save_to_json(book_data)

    print("\n✓ Data saved to my_learning_content/")


def example_process_for_questions():
    """Example: Process scraped data for question generation"""
    print("\nExample 3: Prepare Data for AI Question Generation")
    print("=" * 60)

    # Load previously scraped AI-ready data
    ai_data_file = "zoho_learn_output/Book_Title_ai_ready_20260106_120000.json"

    try:
        with open(ai_data_file, 'r', encoding='utf-8') as f:
            learning_data = json.load(f)

        print(f"Book: {learning_data['book_title']}")
        print(f"Total Learning Units: {learning_data['summary']['total_learning_units']}")
        print(f"Total Words: {learning_data['summary']['total_words']}")
        print(f"Estimated Reading Time: {learning_data['summary']['estimated_total_reading_time_minutes']} minutes")

        print("\n📝 Generating question prompts for AI...")

        # Generate prompts for each learning unit
        for i, unit in enumerate(learning_data['learning_units'][:3], 1):  # First 3 units
            print(f"\n--- Learning Unit {i}: {unit['title']} ---")

            # Create a prompt for AI question generation
            prompt = f"""
Based on this educational content, generate 5 multiple-choice questions:

**Chapter:** {unit['chapter']}
**Title:** {unit['title']}
**Difficulty:** {unit['metadata']['difficulty']}

**Content:**
{unit['content'][:500]}...  # Truncated for example

Requirements:
1. Create 4 answer options (A, B, C, D) with 1 correct answer
2. Include an explanation for the correct answer
3. Reference specific parts of the content
4. Match the difficulty level: {unit['metadata']['difficulty']}

Spaced Repetition Schedule: Review on days {unit['metadata']['spaced_repetition_intervals']}
"""

            print(f"Prompt generated for: {unit['title']}")
            print(f"Word count: {unit['metadata']['word_count']}")
            print(f"Difficulty: {unit['metadata']['difficulty']}")

            # In a real application, you would send this prompt to Claude/GPT
            # questions = send_to_ai(prompt)

    except FileNotFoundError:
        print(f"Error: Could not find {ai_data_file}")
        print("Please run a scrape first!")


def example_spaced_repetition():
    """Example: Create spaced repetition schedule"""
    print("\nExample 4: Spaced Repetition Learning Schedule")
    print("=" * 60)

    # Sample learning unit
    learning_unit = {
        "id": "ch1_art1",
        "title": "Introduction to Python",
        "metadata": {
            "difficulty": "easy",
            "spaced_repetition_intervals": [1, 3, 7, 14, 30, 60, 120]
        }
    }

    print(f"Learning Unit: {learning_unit['title']}")
    print(f"Difficulty: {learning_unit['metadata']['difficulty']}")
    print("\nRecommended Review Schedule:")

    from datetime import datetime, timedelta

    start_date = datetime.now()

    for i, interval in enumerate(learning_unit['metadata']['spaced_repetition_intervals'], 1):
        review_date = start_date + timedelta(days=interval)
        print(f"  Review {i}: Day {interval} - {review_date.strftime('%Y-%m-%d (%A)')}")


def example_analyze_content():
    """Example: Analyze scraped content"""
    print("\nExample 5: Content Analysis")
    print("=" * 60)

    ai_data_file = "zoho_learn_output/Book_Title_ai_ready_20260106_120000.json"

    try:
        with open(ai_data_file, 'r', encoding='utf-8') as f:
            learning_data = json.load(f)

        # Analyze content
        total_words = 0
        difficulty_counts = {"easy": 0, "medium": 0, "hard": 0}
        total_images = 0

        for unit in learning_data['learning_units']:
            total_words += unit['metadata']['word_count']
            difficulty = unit['metadata']['difficulty']
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
            total_images += len(unit['images'])

        print(f"Book: {learning_data['book_title']}")
        print(f"\nContent Statistics:")
        print(f"  Total Words: {total_words:,}")
        print(f"  Average Words per Unit: {total_words // len(learning_data['learning_units']):,}")
        print(f"  Total Images: {total_images}")
        print(f"\nDifficulty Distribution:")
        print(f"  Easy: {difficulty_counts.get('easy', 0)} units")
        print(f"  Medium: {difficulty_counts.get('medium', 0)} units")
        print(f"  Hard: {difficulty_counts.get('hard', 0)} units")

        print(f"\nEstimated Study Time:")
        total_time = learning_data['summary']['estimated_total_reading_time_minutes']
        print(f"  Reading: {total_time} minutes ({total_time // 60}h {total_time % 60}m)")
        print(f"  With review: ~{total_time * 2} minutes (reading + practice)")

    except FileNotFoundError:
        print(f"Error: Could not find {ai_data_file}")
        print("Please run a scrape first!")


def example_export_for_anki():
    """Example: Export data in Anki-compatible format"""
    print("\nExample 6: Export for Anki/Flashcard Apps")
    print("=" * 60)

    # Sample structure for Anki import
    anki_cards = []

    # Sample learning unit (in real use, load from scraped data)
    learning_unit = {
        "id": "ch1_art1",
        "chapter": "Introduction",
        "title": "Python Basics",
        "content": "Python is a high-level programming language...",
        "metadata": {
            "spaced_repetition_intervals": [1, 3, 7, 14, 30]
        }
    }

    # Create flashcard format
    card = {
        "Front": f"{learning_unit['chapter']}: {learning_unit['title']}",
        "Back": learning_unit['content'][:200] + "...",
        "Tags": f"chapter:{learning_unit['chapter']}, id:{learning_unit['id']}",
        "Intervals": learning_unit['metadata']['spaced_repetition_intervals']
    }

    anki_cards.append(card)

    print("Anki Card Format:")
    print(json.dumps(card, indent=2))

    # Save to CSV for Anki import
    import csv

    with open('anki_import.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        for card in anki_cards:
            writer.writerow([card['Front'], card['Back'], card['Tags']])

    print("\n✓ Exported to anki_import.csv")
    print("Import this file into Anki with tab delimiter")


def main():
    """Run all examples"""
    print("=" * 60)
    print("Zoho Learn Scraper - Usage Examples")
    print("=" * 60)

    # Note: Uncomment the examples you want to run

    # example_basic_scrape()
    # example_custom_output()
    example_process_for_questions()
    example_spaced_repetition()
    # example_analyze_content()
    example_export_for_anki()

    print("\n" + "=" * 60)
    print("Examples Complete!")
    print("=" * 60)
    print("\nTips:")
    print("1. Replace example URLs with your actual Zoho Learn links")
    print("2. Adjust output directories as needed")
    print("3. Integrate with your AI provider (Claude, GPT, etc.)")
    print("4. Build your custom learning application!")


if __name__ == "__main__":
    main()

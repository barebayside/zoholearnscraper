"""
Example usage of the Job Scraper with Selenium support
"""

from job_scraper import JobScraper
import json


def example_simple_scrape():
    """Example: Scrape a job using simple HTTP requests (fast but may not work for JS-heavy sites)"""
    print("="*60)
    print("EXAMPLE 1: Simple HTTP Scraping (No Selenium)")
    print("="*60)

    scraper = JobScraper(use_selenium=False)

    url = "https://www.seek.com.au/job/88185524?ref=recom-homepage&pos=2#sol=72f0f1dcdde1acf2f9f49d039aa750b6cda11ff9"
    job_data = scraper.scrape(url)

    print(json.dumps(job_data, indent=2, ensure_ascii=False))
    scraper.save_to_json(job_data, "job_simple.json")
    print(f"\n✓ Job data saved to job_simple.json")
    scraper.close()


def example_selenium_scrape():
    """Example: Scrape seek.com.au using Selenium (for JavaScript-heavy sites)"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Selenium Scraping (For JavaScript Sites)")
    print("="*60)

    # Initialize scraper with Selenium enabled
    # headless=True: runs browser in background (no GUI)
    # headless=False: opens visible browser window (useful for debugging)
    scraper = JobScraper(use_selenium=True, headless=True)

    # Seek.com.au job URL
    url = "https://www.seek.com.au/job/88185524"

    print(f"\nScraping: {url}")
    print("This may take a few seconds as the browser loads...")

    # Scrape the job posting
    # wait_time: how long to wait for JavaScript to load (default: 5 seconds)
    job_data = scraper.scrape(url, wait_time=5)

    # Display the results
    print("\n" + "-"*60)
    print("SCRAPED JOB INFORMATION")
    print("-"*60)

    # Print formatted output
    if 'error' in job_data:
        print(f"❌ Error: {job_data['error']}")
    else:
        print(f"Job Title: {job_data.get('job_title', 'N/A')}")
        print(f"Company: {job_data.get('company', 'N/A')}")
        print(f"Location: {job_data.get('location', 'N/A')}")
        print(f"Salary: {job_data.get('salary', 'N/A')}")
        print(f"Job Type: {job_data.get('job_type', 'N/A')}")
        print(f"Posted: {job_data.get('posted_date', 'N/A')}")
        print(f"Remote Option: {job_data.get('remote_option', False)}")

        if job_data.get('requirements'):
            print(f"\nRequirements ({len(job_data['requirements'])} found):")
            for req in job_data['requirements'][:3]:  # Show first 3
                print(f"  • {req[:80]}...")

        if job_data.get('skills'):
            print(f"\nSkills ({len(job_data['skills'])} found):")
            for skill in job_data['skills'][:5]:  # Show first 5
                print(f"  • {skill}")

    # Save to JSON file
    scraper.save_to_json(job_data, "seek_job.json")
    print(f"\n✓ Full job data saved to seek_job.json")

    # Clean up (close browser)
    scraper.close()
    print("✓ Browser closed")


def example_batch_scraping():
    """Example: Scrape multiple job postings"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Batch Scraping Multiple Jobs")
    print("="*60)

    job_urls = [
        "https://www.seek.com.au/job/88185524",
        "https://www.seek.com.au/job/88185525",  # Add more URLs here
    ]

    # Use context manager for automatic cleanup
    with JobScraper(use_selenium=True, headless=True) as scraper:
        all_jobs = []

        for i, url in enumerate(job_urls, 1):
            print(f"\n[{i}/{len(job_urls)}] Scraping: {url}")
            job_data = scraper.scrape(url)
            all_jobs.append(job_data)

            # Show brief info
            if 'error' not in job_data:
                print(f"  ✓ {job_data.get('job_title', 'N/A')} at {job_data.get('company', 'N/A')}")
            else:
                print(f"  ❌ Error: {job_data['error']}")

        # Save all jobs to one file
        scraper.save_multiple_to_json(all_jobs, "all_jobs.json")
        print(f"\n✓ All {len(all_jobs)} job postings saved to all_jobs.json")

    # Browser automatically closed when exiting 'with' block
    print("✓ Browser closed automatically")


def main():
    """Run the examples"""

    # Example 1: Simple scraping (no Selenium)
    # Uncomment to run:
    # example_simple_scrape()

    # Example 2: Selenium scraping for seek.com.au
    example_selenium_scrape()

    # Example 3: Batch scraping multiple jobs
    # Uncomment to run:
    # example_batch_scraping()

    print("\n" + "="*60)
    print("DONE! Check the JSON files for complete data.")
    print("="*60)


if __name__ == "__main__":
    main()

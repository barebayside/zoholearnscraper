"""
Zoho Learn Scraper GUI
A graphical interface for scraping educational content from Zoho Learn shared links.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
from datetime import datetime
from pathlib import Path
from zoho_learn_scraper import ZohoLearnScraper


class ZohoLearnScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Zoho Learn Educational Content Scraper")
        self.root.geometry("900x800")

        # Variables
        self.scraping = False
        self.scraper = None

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        """Create all GUI widgets"""

        # Title
        title_label = tk.Label(
            self.root,
            text="Zoho Learn Educational Content Scraper",
            font=("Arial", 18, "bold"),
            pady=10
        )
        title_label.pack()

        subtitle_label = tk.Label(
            self.root,
            text="Extract chapters, articles, and images for AI-powered question generation",
            font=("Arial", 10),
            fg="gray"
        )
        subtitle_label.pack()

        # URL Input Section
        url_frame = ttk.LabelFrame(self.root, text="Zoho Learn Book URL", padding=10)
        url_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(url_frame, text="Paste the shared Zoho Learn book URL below:").pack(anchor="w")

        self.url_entry = tk.Entry(url_frame, font=("Arial", 10))
        self.url_entry.pack(fill="x", pady=5)
        self.url_entry.insert(0, "https://learn.zoho.com/portal/...")  # Placeholder

        # Options Section
        options_frame = ttk.LabelFrame(self.root, text="Scraping Options", padding=10)
        options_frame.pack(fill="x", padx=10, pady=5)

        # Selenium option
        self.use_selenium_var = tk.BooleanVar(value=True)
        selenium_check = ttk.Checkbutton(
            options_frame,
            text="Use Selenium (recommended for Zoho Learn)",
            variable=self.use_selenium_var
        )
        selenium_check.pack(anchor="w")

        # Headless option
        self.headless_var = tk.BooleanVar(value=True)
        headless_check = ttk.Checkbutton(
            options_frame,
            text="Headless mode (run browser in background)",
            variable=self.headless_var
        )
        headless_check.pack(anchor="w")

        # Download images option
        self.download_images_var = tk.BooleanVar(value=True)
        images_check = ttk.Checkbutton(
            options_frame,
            text="Download images (saves images locally for AI context)",
            variable=self.download_images_var
        )
        images_check.pack(anchor="w")

        # Wait time
        wait_frame = tk.Frame(options_frame)
        wait_frame.pack(anchor="w", pady=5)
        tk.Label(wait_frame, text="Wait time per page (seconds):").pack(side="left")
        self.wait_time_var = tk.IntVar(value=5)
        wait_spinbox = ttk.Spinbox(
            wait_frame,
            from_=3,
            to=30,
            textvariable=self.wait_time_var,
            width=5
        )
        wait_spinbox.pack(side="left", padx=5)

        # Output directory
        output_frame = tk.Frame(options_frame)
        output_frame.pack(anchor="w", pady=5, fill="x")
        tk.Label(output_frame, text="Output directory:").pack(side="left")
        self.output_dir_var = tk.StringVar(value="zoho_learn_output")
        output_entry = tk.Entry(output_frame, textvariable=self.output_dir_var, width=30)
        output_entry.pack(side="left", padx=5)
        browse_btn = tk.Button(
            output_frame,
            text="Browse...",
            command=self.browse_output_dir
        )
        browse_btn.pack(side="left")

        # Buttons Section
        button_frame = tk.Frame(self.root, pady=10)
        button_frame.pack(fill="x", padx=10)

        self.scrape_button = tk.Button(
            button_frame,
            text="📚 Scrape Zoho Learn Book",
            command=self.start_scraping,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        self.scrape_button.pack(side="left", padx=5)

        self.clear_button = tk.Button(
            button_frame,
            text="Clear Results",
            command=self.clear_results,
            padx=20,
            pady=10
        )
        self.clear_button.pack(side="left", padx=5)

        self.save_button = tk.Button(
            button_frame,
            text="💾 Save to File",
            command=self.save_to_file,
            padx=20,
            pady=10
        )
        self.save_button.pack(side="left", padx=5)

        # Progress Section
        progress_frame = ttk.LabelFrame(self.root, text="Status", padding=10)
        progress_frame.pack(fill="x", padx=10, pady=5)

        self.status_label = tk.Label(
            progress_frame,
            text="Ready to scrape educational content",
            font=("Arial", 10),
            fg="green"
        )
        self.status_label.pack(anchor="w")

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=300
        )
        self.progress_bar.pack(fill="x", pady=5)

        # Results Section
        results_frame = ttk.LabelFrame(self.root, text="Scraped Data Summary", padding=10)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Scrolled text for results
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=("Courier", 9),
            height=20
        )
        self.results_text.pack(fill="both", expand=True)

        # Store the last scraped data
        self.last_book_data = None

    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)

    def update_status(self, message, color="black"):
        """Update status label"""
        self.status_label.config(text=message, fg=color)

    def start_scraping(self):
        """Start the scraping process in a separate thread"""
        if self.scraping:
            messagebox.showwarning("Already Scraping", "A scraping operation is already in progress.")
            return

        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return

        if not url.startswith("http"):
            messagebox.showerror("Error", "URL must start with http:// or https://")
            return

        if "zoho" not in url.lower() and "learn" not in url.lower():
            response = messagebox.askyesno(
                "Warning",
                "This doesn't look like a Zoho Learn URL. Continue anyway?"
            )
            if not response:
                return

        # Disable scrape button
        self.scrape_button.config(state="disabled")
        self.scraping = True

        # Clear previous results
        self.results_text.delete(1.0, tk.END)

        # Start progress bar
        self.progress_bar.start(10)
        self.update_status("Initializing scraper...", "blue")

        # Run scraping in separate thread to keep GUI responsive
        thread = threading.Thread(target=self.scrape_book, args=(url,))
        thread.daemon = True
        thread.start()

    def scrape_book(self, url):
        """Perform the actual scraping (runs in separate thread)"""
        try:
            # Get options
            use_selenium = self.use_selenium_var.get()
            headless = self.headless_var.get()
            wait_time = self.wait_time_var.get()
            output_dir = self.output_dir_var.get()

            # Update status
            self.root.after(0, self.update_status, f"Creating scraper instance...", "blue")

            # Create scraper
            scraper = ZohoLearnScraper(
                use_selenium=use_selenium,
                headless=headless,
                output_dir=output_dir
            )

            # Update status
            self.root.after(0, self.update_status, f"Fetching book: {url}", "blue")
            self.root.after(0, self.log_progress, "Starting scrape...\n")

            # Scrape the book
            book_data = scraper.scrape_book(url, wait_time=wait_time)

            # Update status
            self.root.after(0, self.update_status, "Saving data...", "blue")

            # Save complete data
            json_path = scraper.save_to_json(book_data)
            self.root.after(0, self.log_progress, f"\n✓ Complete data saved to: {json_path}\n")

            # Save AI-optimized data
            ai_path = scraper.save_for_ai_training(book_data)
            self.root.after(0, self.log_progress, f"✓ AI-ready data saved to: {ai_path}\n")

            # Close scraper
            scraper.close()

            # Store the data
            self.last_book_data = book_data

            # Display results on main thread
            self.root.after(0, self.display_results, book_data)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self.update_status, error_msg, "red")
            self.root.after(0, self.log_progress, f"\n❌ {error_msg}\n")
            self.root.after(0, messagebox.showerror, "Scraping Error", error_msg)

        finally:
            # Re-enable scrape button and stop progress bar
            self.root.after(0, self.scrape_button.config, {"state": "normal"})
            self.root.after(0, self.progress_bar.stop)
            self.scraping = False

    def log_progress(self, message):
        """Log progress message to results text"""
        self.results_text.insert(tk.END, message)
        self.results_text.see(tk.END)

    def display_results(self, book_data):
        """Display scraped data summary in the results text area"""
        self.results_text.delete(1.0, tk.END)

        if 'error' in book_data:
            self.update_status(f"Error: {book_data['error']}", "red")
            self.results_text.insert(tk.END, f"❌ Error: {book_data['error']}\n\n")
            self.results_text.insert(tk.END, json.dumps(book_data, indent=2))
            return

        # Display formatted summary
        self.update_status("✓ Scraping completed successfully!", "green")

        # Header
        self.results_text.insert(tk.END, "=" * 80 + "\n")
        self.results_text.insert(tk.END, "ZOHO LEARN BOOK SUMMARY\n")
        self.results_text.insert(tk.END, "=" * 80 + "\n\n")

        # Book info
        self.results_text.insert(tk.END, f"📚 Book Title: {book_data.get('title', 'N/A')}\n")
        if book_data.get('description'):
            self.results_text.insert(tk.END, f"📝 Description: {book_data['description']}\n")
        self.results_text.insert(tk.END, f"🔗 URL: {book_data.get('url', 'N/A')}\n")
        self.results_text.insert(tk.END, f"📅 Scraped: {book_data.get('scraped_at', 'N/A')}\n\n")

        # Statistics
        metadata = book_data.get('metadata', {})
        self.results_text.insert(tk.END, "📊 STATISTICS:\n")
        self.results_text.insert(tk.END, f"  • Total Chapters: {metadata.get('total_chapters', 0)}\n")
        self.results_text.insert(tk.END, f"  • Total Articles: {metadata.get('total_articles', 0)}\n")
        self.results_text.insert(tk.END, f"  • Total Images: {metadata.get('total_images', 0)}\n")
        self.results_text.insert(tk.END, f"  • Spaced Repetition Ready: {'Yes' if metadata.get('spaced_repetition_ready') else 'No'}\n\n")

        # Chapter breakdown
        self.results_text.insert(tk.END, "📖 CHAPTERS:\n")
        self.results_text.insert(tk.END, "-" * 80 + "\n")

        for chapter in book_data.get('chapters', []):
            self.results_text.insert(tk.END, f"\nChapter {chapter['chapter_number']}: {chapter['title']}\n")
            self.results_text.insert(tk.END, f"  Articles: {len(chapter['articles'])}\n")

            # List articles
            for article in chapter['articles']:
                word_count = article.get('metadata', {}).get('word_count', 0)
                reading_time = article.get('metadata', {}).get('estimated_reading_time_minutes', 0)
                num_images = len(article.get('content', {}).get('images', []))

                self.results_text.insert(
                    tk.END,
                    f"    • {article['title']} ({word_count} words, {reading_time} min read, {num_images} images)\n"
                )

        # Content preview
        self.results_text.insert(tk.END, f"\n{'-' * 80}\n")
        self.results_text.insert(tk.END, "📄 CONTENT PREVIEW (First Article):\n")
        self.results_text.insert(tk.END, f"{'-' * 80}\n")

        if book_data.get('chapters') and book_data['chapters'][0].get('articles'):
            first_article = book_data['chapters'][0]['articles'][0]
            self.results_text.insert(tk.END, f"\n{first_article['title']}\n\n")

            # Show first few content items
            structured = first_article.get('content', {}).get('structured', [])
            for item in structured[:10]:
                if item['type'] == 'heading':
                    self.results_text.insert(tk.END, f"\n{'#' * item['level']} {item['text']}\n")
                elif item['type'] == 'paragraph':
                    text = item['text'][:200] + "..." if len(item['text']) > 200 else item['text']
                    self.results_text.insert(tk.END, f"{text}\n\n")
                elif item['type'] == 'list':
                    for list_item in item['items'][:5]:
                        self.results_text.insert(tk.END, f"  • {list_item}\n")

            if len(structured) > 10:
                self.results_text.insert(tk.END, f"\n... and {len(structured) - 10} more content items\n")

        # Output info
        self.results_text.insert(tk.END, f"\n{'-' * 80}\n")
        self.results_text.insert(tk.END, "💾 OUTPUT FILES:\n")
        self.results_text.insert(tk.END, f"{'-' * 80}\n")
        output_dir = self.output_dir_var.get()
        self.results_text.insert(tk.END, f"All data saved to directory: {output_dir}/\n")
        self.results_text.insert(tk.END, f"  • Complete data: JSON file with full structure\n")
        self.results_text.insert(tk.END, f"  • AI-ready data: Optimized JSON for question generation\n")
        self.results_text.insert(tk.END, f"  • Images: {output_dir}/images/\n\n")

        self.results_text.insert(tk.END, "✓ Ready for AI-powered question generation and spaced repetition learning!\n")

        # Scroll to top
        self.results_text.see(1.0)

    def clear_results(self):
        """Clear the results text area"""
        self.results_text.delete(1.0, tk.END)
        self.last_book_data = None
        self.update_status("Ready to scrape educational content", "green")

    def save_to_file(self):
        """Save the last scraped data to a JSON file"""
        if not self.last_book_data:
            messagebox.showwarning("No Data", "No scraped data to save. Please scrape a book first.")
            return

        # Generate default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        book_title = self.last_book_data.get('title', 'zoho_learn_book')
        # Clean book title for filename
        book_title_clean = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).strip()
        book_title_clean = book_title_clean[:50]  # Limit length
        default_filename = f"{book_title_clean}_{timestamp}.json"

        # Ask user where to save
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=default_filename,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.last_book_data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Success", f"Data saved to:\n{filepath}")
                self.update_status(f"Saved to: {filepath}", "green")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file:\n{str(e)}")


def main():
    """Run the GUI application"""
    root = tk.Tk()
    app = ZohoLearnScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

"""
Batch Job Scraper GUI
Scrape multiple job posting URLs at once and save to individual JSON files.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
import os
import re
from datetime import datetime
from job_scraper import JobScraper


class BatchScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Job Scraper")
        self.root.geometry("900x800")

        # Variables
        self.scraping = False
        self.scraper = None
        self.scraped_jobs = []
        self.current_batch_folder = None

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        """Create all GUI widgets"""

        # Title
        title_label = tk.Label(
            self.root,
            text="Batch Job Scraper",
            font=("Arial", 18, "bold"),
            pady=10
        )
        title_label.pack()

        subtitle_label = tk.Label(
            self.root,
            text="Scrape multiple job postings at once - one JSON file per job",
            font=("Arial", 10),
            fg="gray"
        )
        subtitle_label.pack()

        # URL Input Section
        url_frame = ttk.LabelFrame(self.root, text="Job URLs (One per line)", padding=10)
        url_frame.pack(fill="both", expand=True, padx=10, pady=5)

        tk.Label(
            url_frame,
            text="Paste multiple job URLs below (one per line):"
        ).pack(anchor="w")

        # Scrolled text for multiple URLs
        self.urls_text = scrolledtext.ScrolledText(
            url_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            height=8
        )
        self.urls_text.pack(fill="both", expand=True, pady=5)

        # Add example URLs
        example_urls = """https://www.seek.com.au/job/88185524
https://www.seek.com.au/job/88185525
https://www.seek.com.au/job/88185526"""
        self.urls_text.insert(1.0, example_urls)

        # Quick actions
        button_row = tk.Frame(url_frame)
        button_row.pack(fill="x", pady=5)

        tk.Button(
            button_row,
            text="Clear URLs",
            command=lambda: self.urls_text.delete(1.0, tk.END)
        ).pack(side="left", padx=2)

        tk.Button(
            button_row,
            text="Load from File",
            command=self.load_urls_from_file
        ).pack(side="left", padx=2)

        # URL count
        self.url_count_label = tk.Label(button_row, text="URLs: 0", fg="blue")
        self.url_count_label.pack(side="right", padx=5)

        tk.Button(
            button_row,
            text="Count URLs",
            command=self.count_urls
        ).pack(side="right", padx=2)

        # Options Section
        options_frame = ttk.LabelFrame(self.root, text="Scraping Options", padding=10)
        options_frame.pack(fill="x", padx=10, pady=5)

        # Selenium option
        self.use_selenium_var = tk.BooleanVar(value=True)
        selenium_check = ttk.Checkbutton(
            options_frame,
            text="Use Selenium (recommended for seek.com.au)",
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

        # Wait time
        wait_frame = tk.Frame(options_frame)
        wait_frame.pack(anchor="w", pady=5)
        tk.Label(wait_frame, text="Wait time per page (seconds):").pack(side="left")
        self.wait_time_var = tk.IntVar(value=5)
        wait_spinbox = ttk.Spinbox(
            wait_frame,
            from_=1,
            to=30,
            textvariable=self.wait_time_var,
            width=5
        )
        wait_spinbox.pack(side="left", padx=5)

        # Output folder
        folder_frame = tk.Frame(options_frame)
        folder_frame.pack(fill="x", pady=5)
        tk.Label(folder_frame, text="Save to folder:").pack(side="left")
        self.output_folder_var = tk.StringVar(value="batches/")
        tk.Entry(
            folder_frame,
            textvariable=self.output_folder_var,
            width=30
        ).pack(side="left", padx=5)
        tk.Button(
            folder_frame,
            text="Browse",
            command=self.browse_output_folder
        ).pack(side="left")

        # Buttons Section
        button_frame = tk.Frame(self.root, pady=10)
        button_frame.pack(fill="x", padx=10)

        self.scrape_button = tk.Button(
            button_frame,
            text="🚀 Start Batch Scraping",
            command=self.start_batch_scraping,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        self.scrape_button.pack(side="left", padx=5)

        self.stop_button = tk.Button(
            button_frame,
            text="⏹ Stop",
            command=self.stop_scraping,
            state="disabled",
            padx=20,
            pady=10
        )
        self.stop_button.pack(side="left", padx=5)

        self.clear_button = tk.Button(
            button_frame,
            text="Clear Log",
            command=self.clear_log,
            padx=20,
            pady=10
        )
        self.clear_button.pack(side="left", padx=5)

        self.open_folder_button = tk.Button(
            button_frame,
            text="📁 Open Output Folder",
            command=self.open_output_folder,
            padx=20,
            pady=10,
            state="disabled"
        )
        self.open_folder_button.pack(side="left", padx=5)

        # Progress Section
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding=10)
        progress_frame.pack(fill="x", padx=10, pady=5)

        self.status_label = tk.Label(
            progress_frame,
            text="Ready to scrape",
            font=("Arial", 10),
            fg="green"
        )
        self.status_label.pack(anchor="w")

        # Progress bar
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill="x", pady=5)

        self.progress_text = tk.Label(
            progress_frame,
            text="0 / 0 jobs scraped",
            font=("Arial", 9),
            fg="gray"
        )
        self.progress_text.pack(anchor="w")

        # Log Section
        log_frame = ttk.LabelFrame(self.root, text="Scraping Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Scrolled text for log
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Courier", 9),
            height=15,
            bg="#f5f5f5"
        )
        self.log_text.pack(fill="both", expand=True)

    def log(self, message, color="black"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

        # Color the last line
        last_line = self.log_text.index("end-1c linestart")
        self.log_text.tag_add(color, last_line, "end-1c")
        self.log_text.tag_config(color, foreground=color)

    def update_status(self, message, color="black"):
        """Update status label"""
        self.status_label.config(text=message, fg=color)

    def count_urls(self):
        """Count and display number of URLs"""
        urls = self.get_urls()
        count = len(urls)
        self.url_count_label.config(text=f"URLs: {count}")
        if count > 0:
            messagebox.showinfo("URL Count", f"Found {count} valid URL(s)")
        else:
            messagebox.showwarning("No URLs", "No valid URLs found. Please paste URLs (one per line)")

    def get_urls(self):
        """Extract and validate URLs from text area"""
        text = self.urls_text.get(1.0, tk.END)
        lines = text.strip().split('\n')

        urls = []
        for line in lines:
            line = line.strip()
            if line and line.startswith('http'):
                urls.append(line)

        return urls

    def load_urls_from_file(self):
        """Load URLs from a text file"""
        filepath = filedialog.askopenfilename(
            title="Select file with URLs",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filepath:
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                self.urls_text.delete(1.0, tk.END)
                self.urls_text.insert(1.0, content)
                self.log(f"Loaded URLs from {filepath}", "green")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

    def browse_output_folder(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder_var.set(folder)

    def sanitize_filename(self, text, max_length=50):
        """Create safe filename from text"""
        # Remove special characters
        text = re.sub(r'[^\w\s-]', '', text)
        # Replace spaces with underscores
        text = re.sub(r'\s+', '_', text)
        # Limit length
        text = text[:max_length]
        return text.lower()

    def start_batch_scraping(self):
        """Start batch scraping process"""
        if self.scraping:
            messagebox.showwarning("Already Scraping", "Batch scraping is already in progress.")
            return

        urls = self.get_urls()
        if not urls:
            messagebox.showerror("No URLs", "Please enter at least one URL")
            return

        # Confirm
        response = messagebox.askyesno(
            "Confirm Batch Scrape",
            f"Start scraping {len(urls)} job posting(s)?\n\nThis may take several minutes."
        )
        if not response:
            return

        # Create batch folder
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        base_folder = self.output_folder_var.get()
        self.current_batch_folder = os.path.join(base_folder, f"batch_{timestamp}")

        try:
            os.makedirs(self.current_batch_folder, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create output folder:\n{str(e)}")
            return

        # Update UI
        self.scraping = True
        self.scraped_jobs = []
        self.scrape_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.log_text.delete(1.0, tk.END)

        self.log(f"Starting batch scrape of {len(urls)} jobs", "blue")
        self.log(f"Output folder: {self.current_batch_folder}", "blue")
        self.log("-" * 80, "gray")

        # Start scraping in thread
        thread = threading.Thread(target=self.batch_scrape, args=(urls,))
        thread.daemon = True
        thread.start()

    def stop_scraping(self):
        """Stop the scraping process"""
        self.scraping = False
        self.log("Stop requested by user...", "orange")

    def batch_scrape(self, urls):
        """Perform batch scraping (runs in separate thread)"""
        total = len(urls)
        use_selenium = self.use_selenium_var.get()
        headless = self.headless_var.get()
        wait_time = self.wait_time_var.get()

        try:
            # Create scraper once for all jobs
            self.root.after(0, self.log, f"Initializing scraper (Selenium: {use_selenium})...", "blue")
            scraper = JobScraper(use_selenium=use_selenium, headless=headless)

            for i, url in enumerate(urls, 1):
                if not self.scraping:
                    self.root.after(0, self.log, "Scraping stopped by user", "orange")
                    break

                # Update progress
                progress = int((i / total) * 100)
                self.root.after(0, self.progress_var.set, progress)
                self.root.after(0, self.progress_text.config, {"text": f"{i} / {total} jobs scraped"})
                self.root.after(0, self.update_status, f"Scraping job {i}/{total}...", "blue")
                self.root.after(0, self.log, f"\n[{i}/{total}] Scraping: {url}", "blue")

                try:
                    # Scrape the job
                    job_data = scraper.scrape(url, wait_time=wait_time)

                    # Generate filename
                    if 'error' in job_data:
                        filename = f"job_{i:03d}_error.json"
                        self.root.after(0, self.log, f"  ❌ Error: {job_data['error']}", "red")
                    else:
                        job_title = job_data.get('job_title', f'job_{i}')
                        company = job_data.get('company', '')

                        # Create filename
                        title_clean = self.sanitize_filename(job_title, 30)
                        company_clean = self.sanitize_filename(company, 20)

                        if company_clean:
                            filename = f"job_{i:03d}_{title_clean}_{company_clean}.json"
                        else:
                            filename = f"job_{i:03d}_{title_clean}.json"

                        self.root.after(0, self.log, f"  ✓ Job Title: {job_data.get('job_title', 'N/A')}", "green")
                        self.root.after(0, self.log, f"  ✓ Company: {job_data.get('company', 'N/A')}", "green")

                    # Save to file
                    filepath = os.path.join(self.current_batch_folder, filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(job_data, f, indent=2, ensure_ascii=False)

                    self.root.after(0, self.log, f"  💾 Saved: {filename}", "green")
                    self.scraped_jobs.append({
                        'url': url,
                        'filename': filename,
                        'success': 'error' not in job_data
                    })

                except Exception as e:
                    error_msg = f"  ❌ Failed: {str(e)}"
                    self.root.after(0, self.log, error_msg, "red")

                    # Save error to file
                    error_data = {
                        'error': str(e),
                        'url': url,
                        'scraped_at': datetime.utcnow().isoformat()
                    }
                    filename = f"job_{i:03d}_error.json"
                    filepath = os.path.join(self.current_batch_folder, filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(error_data, f, indent=2)

                    self.scraped_jobs.append({
                        'url': url,
                        'filename': filename,
                        'success': False
                    })

            # Close scraper
            scraper.close()

            # Summary
            self.root.after(0, self.show_summary)

        except Exception as e:
            error_msg = f"Batch scraping error: {str(e)}"
            self.root.after(0, self.log, error_msg, "red")
            self.root.after(0, messagebox.showerror, "Error", error_msg)

        finally:
            # Re-enable buttons
            self.root.after(0, self.scrape_button.config, {"state": "normal"})
            self.root.after(0, self.stop_button.config, {"state": "disabled"})
            self.root.after(0, self.open_folder_button.config, {"state": "normal"})
            self.scraping = False

    def show_summary(self):
        """Show summary of batch scraping"""
        total = len(self.scraped_jobs)
        successful = sum(1 for job in self.scraped_jobs if job['success'])
        failed = total - successful

        self.log("-" * 80, "gray")
        self.log("BATCH SCRAPING COMPLETE", "blue")
        self.log(f"Total jobs: {total}", "blue")
        self.log(f"Successful: {successful}", "green")
        self.log(f"Failed: {failed}", "red" if failed > 0 else "gray")
        self.log(f"Output folder: {self.current_batch_folder}", "blue")

        # Update status
        if failed == 0:
            self.update_status(f"✓ Complete! {successful} jobs scraped successfully", "green")
        else:
            self.update_status(f"Complete with {failed} error(s). {successful} successful.", "orange")

        # Show message box
        messagebox.showinfo(
            "Batch Scraping Complete",
            f"Scraped {successful} out of {total} jobs\n\nFiles saved to:\n{self.current_batch_folder}"
        )

    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.progress_text.config(text="0 / 0 jobs scraped")
        self.update_status("Ready to scrape", "green")

    def open_output_folder(self):
        """Open the output folder in file explorer"""
        if self.current_batch_folder and os.path.exists(self.current_batch_folder):
            import platform
            import subprocess

            system = platform.system()
            try:
                if system == "Windows":
                    os.startfile(self.current_batch_folder)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", self.current_batch_folder])
                else:  # Linux
                    subprocess.run(["xdg-open", self.current_batch_folder])
            except Exception as e:
                messagebox.showinfo("Folder Path", f"Output folder:\n{self.current_batch_folder}")
        else:
            messagebox.showwarning("No Folder", "No batch folder created yet")


def main():
    """Run the GUI application"""
    root = tk.Tk()
    app = BatchScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

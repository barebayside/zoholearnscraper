"""
Job Scraper GUI
A simple graphical interface for scraping job postings.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
from datetime import datetime
from job_scraper import JobScraper


class JobScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Posting Scraper")
        self.root.geometry("800x700")

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
            text="Job Posting Scraper",
            font=("Arial", 18, "bold"),
            pady=10
        )
        title_label.pack()

        # URL Input Section
        url_frame = ttk.LabelFrame(self.root, text="Job URL", padding=10)
        url_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(url_frame, text="Paste the job posting URL below:").pack(anchor="w")

        self.url_entry = tk.Entry(url_frame, font=("Arial", 10))
        self.url_entry.pack(fill="x", pady=5)
        self.url_entry.insert(0, "https://www.seek.com.au/job/88185524")  # Default example

        # Options Section
        options_frame = ttk.LabelFrame(self.root, text="Scraping Options", padding=10)
        options_frame.pack(fill="x", padx=10, pady=5)

        # Selenium option
        self.use_selenium_var = tk.BooleanVar(value=True)
        selenium_check = ttk.Checkbutton(
            options_frame,
            text="Use Selenium (for JavaScript sites like seek.com.au)",
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
        tk.Label(wait_frame, text="Wait time (seconds):").pack(side="left")
        self.wait_time_var = tk.IntVar(value=5)
        wait_spinbox = ttk.Spinbox(
            wait_frame,
            from_=1,
            to=30,
            textvariable=self.wait_time_var,
            width=5
        )
        wait_spinbox.pack(side="left", padx=5)

        # Buttons Section
        button_frame = tk.Frame(self.root, pady=10)
        button_frame.pack(fill="x", padx=10)

        self.scrape_button = tk.Button(
            button_frame,
            text="🔍 Scrape Job Posting",
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
            text="Ready to scrape",
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
        results_frame = ttk.LabelFrame(self.root, text="Scraped Data", padding=10)
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
        self.last_job_data = None

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

        # Disable scrape button
        self.scrape_button.config(state="disabled")
        self.scraping = True

        # Clear previous results
        self.results_text.delete(1.0, tk.END)

        # Start progress bar
        self.progress_bar.start(10)
        self.update_status("Scraping in progress...", "blue")

        # Run scraping in separate thread to keep GUI responsive
        thread = threading.Thread(target=self.scrape_job, args=(url,))
        thread.daemon = True
        thread.start()

    def scrape_job(self, url):
        """Perform the actual scraping (runs in separate thread)"""
        try:
            # Get options
            use_selenium = self.use_selenium_var.get()
            headless = self.headless_var.get()
            wait_time = self.wait_time_var.get()

            # Update status
            self.root.after(0, self.update_status, f"Initializing scraper (Selenium: {use_selenium})...", "blue")

            # Create scraper
            scraper = JobScraper(use_selenium=use_selenium, headless=headless)

            # Update status
            self.root.after(0, self.update_status, f"Fetching page: {url}", "blue")

            # Scrape the job
            job_data = scraper.scrape(url, wait_time=wait_time)

            # Close scraper
            scraper.close()

            # Store the data
            self.last_job_data = job_data

            # Display results on main thread
            self.root.after(0, self.display_results, job_data)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self.update_status, error_msg, "red")
            self.root.after(0, messagebox.showerror, "Scraping Error", error_msg)

        finally:
            # Re-enable scrape button and stop progress bar
            self.root.after(0, self.scrape_button.config, {"state": "normal"})
            self.root.after(0, self.progress_bar.stop)
            self.scraping = False

    def display_results(self, job_data):
        """Display scraped data in the results text area"""
        self.results_text.delete(1.0, tk.END)

        if 'error' in job_data:
            self.update_status(f"Error: {job_data['error']}", "red")
            self.results_text.insert(tk.END, f"❌ Error: {job_data['error']}\n\n")
            self.results_text.insert(tk.END, json.dumps(job_data, indent=2))
            return

        # Display formatted data
        self.update_status("✓ Scraping completed successfully!", "green")

        # Header
        self.results_text.insert(tk.END, "=" * 80 + "\n")
        self.results_text.insert(tk.END, "JOB POSTING DETAILS\n")
        self.results_text.insert(tk.END, "=" * 80 + "\n\n")

        # Basic info
        self.results_text.insert(tk.END, f"📋 Job Title: {job_data.get('job_title', 'N/A')}\n")
        self.results_text.insert(tk.END, f"🏢 Company: {job_data.get('company', 'N/A')}\n")
        self.results_text.insert(tk.END, f"📍 Location: {job_data.get('location', 'N/A')}\n")
        self.results_text.insert(tk.END, f"💰 Salary: {job_data.get('salary', 'N/A')}\n")
        self.results_text.insert(tk.END, f"💼 Job Type: {job_data.get('job_type', 'N/A')}\n")
        self.results_text.insert(tk.END, f"🏠 Remote Option: {'Yes' if job_data.get('remote_option') else 'No'}\n")
        self.results_text.insert(tk.END, f"📅 Posted: {job_data.get('posted_date', 'N/A')}\n")
        self.results_text.insert(tk.END, f"🔗 URL: {job_data.get('url', 'N/A')}\n")

        # Description
        if job_data.get('description'):
            self.results_text.insert(tk.END, f"\n📝 Description:\n")
            desc = job_data['description'][:500] + "..." if len(job_data['description']) > 500 else job_data['description']
            self.results_text.insert(tk.END, f"{desc}\n")

        # Requirements
        if job_data.get('requirements'):
            self.results_text.insert(tk.END, f"\n✅ Requirements ({len(job_data['requirements'])}):\n")
            for i, req in enumerate(job_data['requirements'][:10], 1):
                self.results_text.insert(tk.END, f"  {i}. {req}\n")
            if len(job_data['requirements']) > 10:
                self.results_text.insert(tk.END, f"  ... and {len(job_data['requirements']) - 10} more\n")

        # Skills
        if job_data.get('skills'):
            self.results_text.insert(tk.END, f"\n🔧 Skills ({len(job_data['skills'])}):\n")
            skills_str = ", ".join(job_data['skills'][:15])
            self.results_text.insert(tk.END, f"  {skills_str}\n")
            if len(job_data['skills']) > 15:
                self.results_text.insert(tk.END, f"  ... and {len(job_data['skills']) - 15} more\n")

        # Responsibilities
        if job_data.get('responsibilities'):
            self.results_text.insert(tk.END, f"\n📌 Responsibilities ({len(job_data['responsibilities'])}):\n")
            for i, resp in enumerate(job_data['responsibilities'][:10], 1):
                self.results_text.insert(tk.END, f"  {i}. {resp}\n")
            if len(job_data['responsibilities']) > 10:
                self.results_text.insert(tk.END, f"  ... and {len(job_data['responsibilities']) - 10} more\n")

        # Benefits
        if job_data.get('benefits'):
            self.results_text.insert(tk.END, f"\n🎁 Benefits ({len(job_data['benefits'])}):\n")
            for i, benefit in enumerate(job_data['benefits'][:10], 1):
                self.results_text.insert(tk.END, f"  {i}. {benefit}\n")
            if len(job_data['benefits']) > 10:
                self.results_text.insert(tk.END, f"  ... and {len(job_data['benefits']) - 10} more\n")

        # Full JSON at the end
        self.results_text.insert(tk.END, f"\n{'-' * 80}\n")
        self.results_text.insert(tk.END, "FULL JSON DATA:\n")
        self.results_text.insert(tk.END, f"{'-' * 80}\n")
        self.results_text.insert(tk.END, json.dumps(job_data, indent=2, ensure_ascii=False))

        # Scroll to top
        self.results_text.see(1.0)

    def clear_results(self):
        """Clear the results text area"""
        self.results_text.delete(1.0, tk.END)
        self.last_job_data = None
        self.update_status("Ready to scrape", "green")

    def save_to_file(self):
        """Save the last scraped data to a JSON file"""
        if not self.last_job_data:
            messagebox.showwarning("No Data", "No scraped data to save. Please scrape a job first.")
            return

        # Generate default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_title = self.last_job_data.get('job_title', 'job')
        # Clean job title for filename
        job_title_clean = "".join(c for c in job_title if c.isalnum() or c in (' ', '-', '_')).strip()
        job_title_clean = job_title_clean[:50]  # Limit length
        default_filename = f"{job_title_clean}_{timestamp}.json"

        # Ask user where to save
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=default_filename,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.last_job_data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Success", f"Data saved to:\n{filepath}")
                self.update_status(f"Saved to: {filepath}", "green")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file:\n{str(e)}")


def main():
    """Run the GUI application"""
    root = tk.Tk()
    app = JobScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

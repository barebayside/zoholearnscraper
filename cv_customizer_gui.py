"""
CV Customizer with Claude API
Load multiple documents about yourself and generate customized CVs for each job.
Now with customizable prompt templates!
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os
import threading
import subprocess
import platform
from datetime import datetime
from pathlib import Path
import base64

# Document parsing imports
try:
    from pypdf import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

from bs4 import BeautifulSoup

# Claude API
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Template directory
PROMPTS_DIR = "prompts"


class CVCustomizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CV Customizer with Claude AI - Template Edition")
        self.root.geometry("1000x700")  # Start at reasonable size
        self.root.minsize(800, 500)  # Minimum window size - scroll to see more

        # Variables
        self.loaded_documents = []
        self.job_files = []
        self.processing = False
        self.api_key = ""
        self.config_file = "cv_customizer_config.json"

        # Template selections
        self.cv_template_files = {
            "Professional (Corporate/Finance)": "cv_professional.txt",
            "Technical (Software/Engineering)": "cv_technical.txt",
            "Creative (Design/Marketing)": "cv_creative.txt"
        }

        self.cover_template_files = {
            "Formal (Corporate)": "cover_letter_formal.txt",
            "Casual (Startup/Tech)": "cover_letter_casual.txt"
        }

        # Create GUI
        self.create_widgets()
        self.check_dependencies()
        self.check_templates()
        self.load_config()  # Load saved settings

    def check_dependencies(self):
        """Check if required libraries are installed"""
        missing = []
        if not ANTHROPIC_AVAILABLE:
            missing.append("anthropic")
        if not PDF_AVAILABLE:
            missing.append("pypdf")
        if not DOCX_AVAILABLE:
            missing.append("python-docx")

        if missing:
            msg = f"Missing libraries: {', '.join(missing)}\n\nPlease install:\npip install {' '.join(missing)}"
            messagebox.showwarning("Missing Dependencies", msg)

    def check_templates(self):
        """Check if template files exist"""
        if not os.path.exists(PROMPTS_DIR):
            messagebox.showwarning(
                "Templates Not Found",
                f"Template directory '{PROMPTS_DIR}/' not found.\n\n"
                "Template files should be in a 'prompts/' folder."
            )

    def create_widgets(self):
        """Create all GUI widgets"""

        # Create a main canvas with scrollbar
        main_canvas = tk.Canvas(self.root, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)

        # Create a frame inside the canvas to hold all content
        scrollable_frame = tk.Frame(main_canvas)

        # Configure the canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        # Create window in canvas
        canvas_frame = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Configure canvas scrolling
        main_canvas.configure(yscrollcommand=scrollbar.set)

        # Bind canvas width to frame width for responsiveness
        def configure_canvas_width(event):
            main_canvas.itemconfig(canvas_frame, width=event.width)
        main_canvas.bind("<Configure>", configure_canvas_width)

        # Pack canvas and scrollbar
        scrollbar.pack(side="right", fill="y")
        main_canvas.pack(side="left", fill="both", expand=True)

        # Mouse wheel scrolling
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def bind_mousewheel(event):
            main_canvas.bind_all("<MouseWheel>", on_mousewheel)

        def unbind_mousewheel(event):
            main_canvas.unbind_all("<MouseWheel>")

        main_canvas.bind("<Enter>", bind_mousewheel)
        main_canvas.bind("<Leave>", unbind_mousewheel)

        # Now use scrollable_frame as the parent for all widgets instead of self.root

        # Title
        title_label = tk.Label(
            scrollable_frame,
            text="CV Customizer with Claude AI",
            font=("Arial", 18, "bold"),
            pady=10
        )
        title_label.pack()

        subtitle_label = tk.Label(
            scrollable_frame,
            text="Upload documents → Select templates → Generate customized CVs",
            font=("Arial", 10),
            fg="gray"
        )
        subtitle_label.pack()

        # Main container with two columns
        main_container = tk.Frame(scrollable_frame)
        main_container.pack(fill="x", padx=10, pady=5)

        # Left column: Your Documents
        left_frame = ttk.LabelFrame(main_container, text="Your Profile Documents", padding=10)
        left_frame.pack(side="left", fill="x", expand=True, padx=5)

        tk.Label(
            left_frame,
            text="Upload documents about yourself (resume, LinkedIn, portfolio, etc.):",
            wraplength=400
        ).pack(anchor="w")

        # Document list
        doc_list_frame = tk.Frame(left_frame)
        doc_list_frame.pack(fill="x", pady=5)

        doc_scrollbar = ttk.Scrollbar(doc_list_frame)
        doc_scrollbar.pack(side="right", fill="y")

        self.doc_listbox = tk.Listbox(
            doc_list_frame,
            yscrollcommand=doc_scrollbar.set,
            height=4
        )
        self.doc_listbox.pack(side="left", fill="both", expand=True)
        doc_scrollbar.config(command=self.doc_listbox.yview)

        # Document buttons
        doc_button_frame = tk.Frame(left_frame)
        doc_button_frame.pack(fill="x", pady=5)

        tk.Button(
            doc_button_frame,
            text="📄 Add Documents",
            command=self.add_documents,
            bg="#4CAF50",
            fg="white",
            padx=10,
            pady=5
        ).pack(side="left", padx=2)

        tk.Button(
            doc_button_frame,
            text="Remove",
            command=self.remove_document,
            padx=10,
            pady=5
        ).pack(side="left", padx=2)

        tk.Button(
            doc_button_frame,
            text="Clear All",
            command=self.clear_documents,
            padx=10,
            pady=5
        ).pack(side="left", padx=2)

        tk.Label(
            left_frame,
            text="Supported: PDF, DOCX, HTML, TXT",
            font=("Arial", 8),
            fg="gray"
        ).pack(anchor="w")

        # Right column: Job Postings
        right_frame = ttk.LabelFrame(main_container, text="Job Postings (JSON Files)", padding=10)
        right_frame.pack(side="left", fill="x", expand=True, padx=5)

        tk.Label(
            right_frame,
            text="Select folder with scraped job JSON files:",
            wraplength=400
        ).pack(anchor="w")

        # Job folder selection
        folder_frame = tk.Frame(right_frame)
        folder_frame.pack(fill="x", pady=5)

        self.job_folder_var = tk.StringVar()
        tk.Entry(
            folder_frame,
            textvariable=self.job_folder_var,
            state="readonly",
            width=30
        ).pack(side="left", fill="x", expand=True, padx=5)

        tk.Button(
            folder_frame,
            text="Browse",
            command=self.select_job_folder,
            padx=10,
            pady=5
        ).pack(side="left")

        # Job list
        job_list_frame = tk.Frame(right_frame)
        job_list_frame.pack(fill="x", pady=5)

        job_scrollbar = ttk.Scrollbar(job_list_frame)
        job_scrollbar.pack(side="right", fill="y")

        self.job_listbox = tk.Listbox(
            job_list_frame,
            yscrollcommand=job_scrollbar.set,
            height=4
        )
        self.job_listbox.pack(side="left", fill="both", expand=True)
        job_scrollbar.config(command=self.job_listbox.yview)

        self.job_count_label = tk.Label(right_frame, text="No jobs loaded", fg="gray")
        self.job_count_label.pack(anchor="w")

        # API Key Section
        api_frame = ttk.LabelFrame(scrollable_frame, text="Claude API Configuration", padding=10)
        api_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(
            api_frame,
            text="Anthropic API Key (get from: https://console.anthropic.com/):"
        ).pack(anchor="w")

        key_entry_frame = tk.Frame(api_frame)
        key_entry_frame.pack(fill="x", pady=5)

        self.api_key_var = tk.StringVar()
        self.api_key_entry = tk.Entry(
            key_entry_frame,
            textvariable=self.api_key_var,
            show="*",
            font=("Arial", 10)
        )
        self.api_key_entry.pack(side="left", fill="x", expand=True, padx=5)

        self.show_key_var = tk.BooleanVar()
        tk.Checkbutton(
            key_entry_frame,
            text="Show",
            variable=self.show_key_var,
            command=self.toggle_api_key_visibility
        ).pack(side="left")

        self.save_key_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            key_entry_frame,
            text="Remember API Key",
            variable=self.save_key_var
        ).pack(side="left", padx=5)

        tk.Button(
            key_entry_frame,
            text="Test API Key",
            command=self.test_api_key,
            padx=10,
            pady=5
        ).pack(side="left", padx=5)

        # Template Selection Section
        template_frame = ttk.LabelFrame(scrollable_frame, text="📝 Template Selection", padding=10)
        template_frame.pack(fill="x", padx=10, pady=5)

        # CV Template
        cv_template_row = tk.Frame(template_frame)
        cv_template_row.pack(fill="x", pady=3)

        tk.Label(cv_template_row, text="CV Style:", width=15, anchor="w").pack(side="left", padx=5)
        self.cv_template_var = tk.StringVar(value="Professional (Corporate/Finance)")
        ttk.Combobox(
            cv_template_row,
            textvariable=self.cv_template_var,
            values=list(self.cv_template_files.keys()),
            state="readonly",
            width=35
        ).pack(side="left", padx=5)

        tk.Button(
            cv_template_row,
            text="✏️ Edit Template",
            command=lambda: self.edit_template("cv"),
            padx=10,
            pady=3
        ).pack(side="left", padx=5)

        # Cover Letter Template
        cover_template_row = tk.Frame(template_frame)
        cover_template_row.pack(fill="x", pady=3)

        tk.Label(cover_template_row, text="Cover Letter:", width=15, anchor="w").pack(side="left", padx=5)
        self.cover_template_var = tk.StringVar(value="Formal (Corporate)")
        ttk.Combobox(
            cover_template_row,
            textvariable=self.cover_template_var,
            values=list(self.cover_template_files.keys()),
            state="readonly",
            width=35
        ).pack(side="left", padx=5)

        tk.Button(
            cover_template_row,
            text="✏️ Edit Template",
            command=lambda: self.edit_template("cover"),
            padx=10,
            pady=3
        ).pack(side="left", padx=5)

        # Template info
        tk.Label(
            template_frame,
            text="💡 Tip: Edit templates to customize output style and formatting",
            font=("Arial", 8),
            fg="blue"
        ).pack(anchor="w", pady=5)

        # Options Section
        options_frame = ttk.LabelFrame(scrollable_frame, text="Generation Options", padding=10)
        options_frame.pack(fill="x", padx=10, pady=5)

        # What to generate
        gen_frame = tk.Frame(options_frame)
        gen_frame.pack(fill="x")

        tk.Label(gen_frame, text="Generate:").pack(side="left", padx=5)

        self.gen_cv_var = tk.BooleanVar(value=True)
        tk.Checkbutton(gen_frame, text="Customized CV", variable=self.gen_cv_var).pack(side="left", padx=5)

        self.gen_cover_var = tk.BooleanVar(value=True)
        tk.Checkbutton(gen_frame, text="Cover Letter", variable=self.gen_cover_var).pack(side="left", padx=5)

        self.gen_talking_var = tk.BooleanVar(value=False)
        tk.Checkbutton(gen_frame, text="Interview Talking Points", variable=self.gen_talking_var).pack(side="left", padx=5)

        # Company research option
        self.research_company_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            gen_frame,
            text="🔍 Research Company (adds values/philosophy)",
            variable=self.research_company_var
        ).pack(side="left", padx=5)

        # Model selection
        model_frame = tk.Frame(options_frame)
        model_frame.pack(fill="x", pady=5)

        tk.Label(model_frame, text="Claude Model:").pack(side="left", padx=5)
        self.model_var = tk.StringVar(value="Claude Haiku 3 (claude-3-haiku-20240307)")
        
        # Model options with display names and ACTUAL API model names
        model_options = [
            "Claude Haiku 3 (claude-3-haiku-20240307)",
            "Claude Haiku 3.5 (claude-3-5-haiku-20241022)",
            "Claude Haiku 4.5 (claude-haiku-4-5-20251001)",
            "Claude Sonnet 3.5 (claude-3-5-sonnet-20241022)",
            "Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)",
            "Claude Opus 3 (claude-3-opus-20240229)",
            "Claude Opus 4.1 (claude-opus-4-1-20250805)"
        ]
        
        ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=model_options,
            state="readonly",
            width=45
        ).pack(side="left", padx=5)

        # Output folder
        output_frame = tk.Frame(options_frame)
        output_frame.pack(fill="x", pady=5)

        tk.Label(output_frame, text="Output folder:").pack(side="left", padx=5)
        self.output_folder_var = tk.StringVar(value="customized_cvs/")
        tk.Entry(output_frame, textvariable=self.output_folder_var, width=30).pack(side="left", padx=5)
        tk.Button(output_frame, text="Browse", command=self.browse_output_folder).pack(side="left")

        # Action Buttons
        button_frame = tk.Frame(scrollable_frame, pady=10)
        button_frame.pack(fill="x", padx=10)

        self.generate_button = tk.Button(
            button_frame,
            text="🚀 Generate Customized CVs",
            command=self.start_generation,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        self.generate_button.pack(side="left", padx=5)

        self.stop_button = tk.Button(
            button_frame,
            text="⏹ Stop",
            command=self.stop_generation,
            state="disabled",
            padx=20,
            pady=10
        )
        self.stop_button.pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="Clear Log",
            command=self.clear_log,
            padx=20,
            pady=10
        ).pack(side="left", padx=5)

        self.open_output_button = tk.Button(
            button_frame,
            text="📁 Open Output Folder",
            command=self.open_output_folder,
            padx=20,
            pady=10,
            state="disabled"
        )
        self.open_output_button.pack(side="left", padx=5)

        # Progress Section
        progress_frame = ttk.LabelFrame(scrollable_frame, text="Progress", padding=10)
        progress_frame.pack(fill="x", padx=10, pady=5)

        self.status_label = tk.Label(
            progress_frame,
            text="Ready to generate customized CVs",
            font=("Arial", 10),
            fg="green"
        )
        self.status_label.pack(anchor="w")

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
            text="0 / 0 CVs generated",
            font=("Arial", 9),
            fg="gray"
        )
        self.progress_text.pack(anchor="w")

        # Log Section
        log_frame = ttk.LabelFrame(scrollable_frame, text="Generation Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Courier", 9),
            height=6,
            bg="#f5f5f5"
        )
        self.log_text.pack(fill="both", expand=True)

    def log(self, message, color="black"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

        last_line = self.log_text.index("end-1c linestart")
        self.log_text.tag_add(color, last_line, "end-1c")
        self.log_text.tag_config(color, foreground=color)

    def update_status(self, message, color="black"):
        """Update status label"""
        self.status_label.config(text=message, fg=color)

    def toggle_api_key_visibility(self):
        """Toggle API key visibility"""
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")

    def save_config(self):
        """Save API key and settings to config file"""
        try:
            config = {}

            # Save API key if checkbox is checked
            if self.save_key_var.get():
                api_key = self.api_key_var.get().strip()
                if api_key:
                    # Simple encoding (not encryption, just obfuscation)
                    encoded_key = base64.b64encode(api_key.encode()).decode()
                    config['api_key'] = encoded_key

            # Save other settings
            config['output_folder'] = self.output_folder_var.get()
            config['model'] = self.model_var.get()
            config['gen_cv'] = self.gen_cv_var.get()
            config['gen_cover'] = self.gen_cover_var.get()
            config['gen_talking'] = self.gen_talking_var.get()

            with open(self.config_file, 'w') as f:
                json.dump(config, f)

        except Exception as e:
            print(f"Warning: Could not save config: {e}")

    def load_config(self):
        """Load API key and settings from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)

                # Load API key
                if 'api_key' in config:
                    try:
                        decoded_key = base64.b64decode(config['api_key'].encode()).decode()
                        self.api_key_var.set(decoded_key)
                        self.log("✓ API key loaded from saved settings", "green")
                    except:
                        pass

                # Load other settings
                if 'output_folder' in config:
                    self.output_folder_var.set(config['output_folder'])
                if 'model' in config:
                    self.model_var.set(config['model'])
                if 'gen_cv' in config:
                    self.gen_cv_var.set(config['gen_cv'])
                if 'gen_cover' in config:
                    self.gen_cover_var.set(config['gen_cover'])
                if 'gen_talking' in config:
                    self.gen_talking_var.set(config['gen_talking'])

        except Exception as e:
            print(f"Warning: Could not load config: {e}")

    def edit_template(self, template_type):
        """Open template file in default text editor"""
        if template_type == "cv":
            template_name = self.cv_template_var.get()
            template_file = self.cv_template_files.get(template_name)
        elif template_type == "cover":
            template_name = self.cover_template_var.get()
            template_file = self.cover_template_files.get(template_name)
        else:
            return

        template_path = os.path.join(PROMPTS_DIR, template_file)

        if not os.path.exists(template_path):
            messagebox.showerror(
                "Template Not Found",
                f"Template file not found:\n{template_path}\n\n"
                "Make sure template files are in the 'prompts/' folder."
            )
            return

        try:
            # Open file in default editor
            system = platform.system()
            if system == "Windows":
                os.startfile(template_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", template_path])
            else:  # Linux
                subprocess.run(["xdg-open", template_path])

            self.log(f"Opened template: {template_file}", "blue")
            messagebox.showinfo(
                "Template Opened",
                f"Template opened in your default text editor.\n\n"
                f"Edit and save the file, then generate CVs to see your changes."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open template:\n{str(e)}")

    def load_template(self, template_file):
        """Load template content from file"""
        template_path = os.path.join(PROMPTS_DIR, template_file)

        if not os.path.exists(template_path):
            self.log(f"Warning: Template {template_file} not found, using default", "orange")
            return None

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.log(f"Error loading template {template_file}: {str(e)}", "red")
            return None

    def research_company(self, company_name, client, model):
        """Research company to find values, philosophy, and culture"""
        if not company_name or company_name == 'Unknown Company':
            return None

        try:
            # Use Claude to research the company via web search or knowledge
            research_prompt = f"""Please provide a brief overview of {company_name}, focusing on:
1. Company values and mission
2. Company culture and philosophy
3. Key products/services
4. Recent news or achievements (if known)

Keep it concise (3-4 sentences total). If you don't have specific information, say "No specific information available."
"""

            response = client.messages.create(
                model=model,
                max_tokens=500,
                messages=[{"role": "user", "content": research_prompt}]
            )

            company_info = response.content[0].text

            # Check if we got useful information
            if "no specific information" in company_info.lower() or "don't have" in company_info.lower():
                return None

            return company_info

        except Exception as e:
            print(f"DEBUG: Company research error: {e}")
            return None

    def fill_template(self, template, profile, job_data, company_info=None):
        """Fill template with actual values"""
        if template is None:
            return None

        # Replace placeholders
        filled = template.replace("{profile}", profile)
        filled = filled.replace("{job_title}", job_data.get('job_title', 'Unknown Position'))
        filled = filled.replace("{company}", job_data.get('company', 'Unknown Company'))
        filled = filled.replace("{location}", job_data.get('location', 'N/A'))
        filled = filled.replace("{requirements}", json.dumps(job_data.get('requirements', []), indent=2))
        filled = filled.replace("{skills}", json.dumps(job_data.get('skills', []), indent=2))
        filled = filled.replace("{responsibilities}", json.dumps(job_data.get('responsibilities', []), indent=2))
        filled = filled.replace("{description}", job_data.get('description', 'N/A'))

        # Add company research if available
        if company_info:
            company_section = f"\n\nCOMPANY RESEARCH:\n{company_info}\n\nUse this information to demonstrate knowledge of the company's values and culture in your response."
            filled = filled.replace("{company_research}", company_section)
        else:
            filled = filled.replace("{company_research}", "")

        return filled

    def add_documents(self):
        """Add profile documents"""
        filetypes = [
            ("All supported", "*.pdf *.docx *.html *.htm *.txt"),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx"),
            ("HTML files", "*.html *.htm"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]

        files = filedialog.askopenfilenames(
            title="Select Profile Documents",
            filetypes=filetypes
        )

        for filepath in files:
            if filepath not in self.loaded_documents:
                self.loaded_documents.append(filepath)
                filename = os.path.basename(filepath)
                self.doc_listbox.insert(tk.END, filename)
                self.log(f"Added document: {filename}", "green")

    def remove_document(self):
        """Remove selected document"""
        selection = self.doc_listbox.curselection()
        if selection:
            index = selection[0]
            filename = self.doc_listbox.get(index)
            self.doc_listbox.delete(index)
            del self.loaded_documents[index]
            self.log(f"Removed document: {filename}", "orange")

    def clear_documents(self):
        """Clear all documents"""
        self.doc_listbox.delete(0, tk.END)
        self.loaded_documents.clear()
        self.log("Cleared all documents", "gray")

    def select_job_folder(self):
        """Select folder with job JSON files"""
        folder = filedialog.askdirectory(title="Select Folder with Job JSON Files")

        if folder:
            self.job_folder_var.set(folder)
            self.load_job_files(folder)

    def load_job_files(self, folder):
        """Load job JSON files from folder"""
        self.job_listbox.delete(0, tk.END)
        self.job_files.clear()

        try:
            json_files = [f for f in os.listdir(folder) if f.endswith('.json')]

            for filename in sorted(json_files):
                filepath = os.path.join(folder, filename)
                self.job_files.append(filepath)
                self.job_listbox.insert(tk.END, filename)

            count = len(json_files)
            self.job_count_label.config(text=f"{count} job(s) loaded", fg="green")
            self.log(f"Loaded {count} job file(s) from {folder}", "green")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load job files:\n{str(e)}")

    def browse_output_folder(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder_var.set(folder)

    def test_api_key(self):
        """Test the Claude API key"""
        api_key = self.api_key_var.get().strip()

        if not api_key:
            messagebox.showerror("Error", "Please enter an API key")
            return

        if not ANTHROPIC_AVAILABLE:
            messagebox.showerror("Error", "Anthropic library not installed.\nRun: pip install anthropic")
            return

        try:
            self.log("Testing API key...", "blue")
            client = Anthropic(api_key=api_key)

            # Simple test message
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Say 'OK'"}]
            )

            self.log("✓ API key is valid!", "green")
            messagebox.showinfo("Success", "API key is valid and working!")

        except Exception as e:
            self.log(f"✗ API key test failed: {str(e)}", "red")
            messagebox.showerror("API Key Error", f"Failed to validate API key:\n\n{str(e)}")

    def read_document(self, filepath):
        """Read content from various document formats"""
        ext = os.path.splitext(filepath)[1].lower()

        try:
            if ext == '.pdf':
                return self.read_pdf(filepath)
            elif ext == '.docx':
                return self.read_docx(filepath)
            elif ext in ['.html', '.htm']:
                return self.read_html(filepath)
            elif ext == '.txt':
                return self.read_txt(filepath)
            else:
                return f"[Unsupported file type: {ext}]"
        except Exception as e:
            return f"[Error reading file: {str(e)}]"

    def read_pdf(self, filepath):
        """Read PDF file"""
        if not PDF_AVAILABLE:
            return "[PDF support not installed. Run: pip install pypdf]"

        try:
            reader = PdfReader(filepath)
            text = []
            for page in reader.pages:
                text.append(page.extract_text())
            return "\n\n".join(text)
        except Exception as e:
            return f"[Error reading PDF: {str(e)}]"

    def read_docx(self, filepath):
        """Read Word document"""
        if not DOCX_AVAILABLE:
            return "[DOCX support not installed. Run: pip install python-docx]"

        try:
            doc = Document(filepath)
            text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text.append(para.text)
            return "\n\n".join(text)
        except Exception as e:
            return f"[Error reading DOCX: {str(e)}]"

    def read_html(self, filepath):
        """Read HTML file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                html = f.read()
            soup = BeautifulSoup(html, 'lxml')
            # Remove script and style
            for script in soup(['script', 'style']):
                script.decompose()
            return soup.get_text(separator='\n', strip=True)
        except Exception as e:
            return f"[Error reading HTML: {str(e)}]"

    def read_txt(self, filepath):
        """Read text file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"[Error reading TXT: {str(e)}]"

    def start_generation(self):
        """Start CV generation process"""
        # Validation
        if not self.loaded_documents:
            messagebox.showerror("Error", "Please add at least one profile document")
            return

        if not self.job_files:
            messagebox.showerror("Error", "Please select a folder with job JSON files")
            return

        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter your Claude API key")
            return

        if not ANTHROPIC_AVAILABLE:
            messagebox.showerror("Error", "Anthropic library not installed.\nRun: pip install anthropic")
            return

        if not (self.gen_cv_var.get() or self.gen_cover_var.get() or self.gen_talking_var.get()):
            messagebox.showerror("Error", "Please select at least one type of content to generate")
            return

        # Confirm
        response = messagebox.askyesno(
            "Confirm Generation",
            f"Generate customized content for {len(self.job_files)} job(s)?\n\n"
            f"Using {len(self.loaded_documents)} profile document(s)\n"
            f"CV Template: {self.cv_template_var.get()}\n"
            f"Cover Template: {self.cover_template_var.get()}\n\n"
            f"This will use Claude API credits."
        )
        if not response:
            return

        # Save config before starting
        self.save_config()

        # Create output folder
        output_folder = self.output_folder_var.get()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.current_output_folder = os.path.join(output_folder, f"batch_{timestamp}")

        try:
            os.makedirs(self.current_output_folder, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create output folder:\n{str(e)}")
            return

        # Update UI
        self.processing = True
        self.generate_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.log_text.delete(1.0, tk.END)

        self.log(f"Starting CV generation for {len(self.job_files)} job(s)", "blue")
        self.log(f"Output folder: {self.current_output_folder}", "blue")
        self.log(f"CV Template: {self.cv_template_var.get()}", "blue")
        self.log(f"Cover Template: {self.cover_template_var.get()}", "blue")
        self.log("-" * 80, "gray")

        # Start in thread
        thread = threading.Thread(target=self.generate_cvs, args=(api_key,))
        thread.daemon = True
        thread.start()

    def stop_generation(self):
        """Stop generation"""
        self.processing = False
        self.log("Stop requested by user...", "orange")

    def generate_cvs(self, api_key):
        """Generate customized CVs (runs in thread)"""
        try:
            # Initialize Claude client
            print("DEBUG: Starting generate_cvs thread")  # DEBUG
            self.root.after(0, self.log, "Initializing Claude API client...", "blue")
            
            # Extract model name from dropdown selection (format: "Display Name (model-name)")
            model_selection = self.model_var.get()
            if "(" in model_selection and ")" in model_selection:
                model = model_selection.split("(")[1].split(")")[0]
            else:
                model = model_selection  # Fallback to direct value
            
            self.root.after(0, self.log, f"Using model: {model}", "gray")
            
            try:
                client = Anthropic(api_key=api_key)
                print(f"DEBUG: API client created, model={model}")  # DEBUG
                self.root.after(0, self.log, "✓ API client initialized", "green")
            except Exception as api_init_error:
                print(f"DEBUG: API init failed: {api_init_error}")  # DEBUG
                self.root.after(0, self.log, f"✗ Failed to initialize API: {str(api_init_error)}", "red")
                raise

            # Step 1: Read all profile documents
            print(f"DEBUG: Loading {len(self.loaded_documents)} profile documents")  # DEBUG
            self.root.after(0, self.log, "\nStep 1: Reading your profile documents...", "blue")

            profile_content = []
            for i, filepath in enumerate(self.loaded_documents, 1):
                filename = os.path.basename(filepath)
                print(f"DEBUG: Reading document {i}: {filename}")  # DEBUG
                self.root.after(0, self.log, f"  Reading {i}/{len(self.loaded_documents)}: {filename}", "gray")

                content = self.read_document(filepath)
                print(f"DEBUG: Document content length: {len(content)}")  # DEBUG
                profile_content.append(f"=== Document: {filename} ===\n{content}")

            combined_profile = "\n\n".join(profile_content)
            print(f"DEBUG: Combined profile length: {len(combined_profile)}")  # DEBUG
            self.root.after(0, self.log, f"✓ Loaded {len(self.loaded_documents)} document(s)", "green")

            # Step 2: Load templates
            self.root.after(0, self.log, "\nStep 2: Loading templates...", "blue")

            cv_template_name = self.cv_template_files.get(self.cv_template_var.get())
            cover_template_name = self.cover_template_files.get(self.cover_template_var.get())

            cv_template = self.load_template(cv_template_name) if self.gen_cv_var.get() else None
            cover_template = self.load_template(cover_template_name) if self.gen_cover_var.get() else None
            talking_template = self.load_template("talking_points.txt") if self.gen_talking_var.get() else None

            if cv_template:
                self.root.after(0, self.log, f"  ✓ Loaded CV template: {cv_template_name}", "green")
            if cover_template:
                self.root.after(0, self.log, f"  ✓ Loaded cover letter template: {cover_template_name}", "green")
            if talking_template:
                self.root.after(0, self.log, f"  ✓ Loaded talking points template", "green")

            # Step 3: Process each job
            total_jobs = len(self.job_files)
            print(f"DEBUG: Processing {total_jobs} job files")  # DEBUG
            self.root.after(0, self.log, f"\nStep 3: Generating customized content for {total_jobs} job(s)...", "blue")

            for i, job_filepath in enumerate(self.job_files, 1):
                if not self.processing:
                    break

                # Update progress
                progress = int((i / total_jobs) * 100)
                self.root.after(0, self.progress_var.set, progress)
                self.root.after(0, self.progress_text.config, {"text": f"{i} / {total_jobs} CVs generated"})

                job_filename = os.path.basename(job_filepath)
                print(f"DEBUG: [{i}/{total_jobs}] Processing job: {job_filename}")  # DEBUG
                self.root.after(0, self.log, f"\n[{i}/{total_jobs}] Processing: {job_filename}", "blue")

                try:
                    # Load job JSON
                    with open(job_filepath, 'r', encoding='utf-8') as f:
                        job_data = json.load(f)

                    if 'error' in job_data:
                        self.root.after(0, self.log, f"  ⚠ Skipping (error in job data)", "orange")
                        continue

                    # Research company if enabled
                    company_info = None
                    if self.research_company_var.get():
                        company_name = job_data.get('company', 'Unknown Company')
                        if company_name and company_name != 'Unknown Company':
                            self.root.after(0, self.log, f"  🔍 Researching {company_name}...", "blue")
                            try:
                                company_info = self.research_company(company_name, client, model)
                                if company_info:
                                    self.root.after(0, self.log, f"  ✓ Company research completed", "green")
                                else:
                                    self.root.after(0, self.log, f"  ℹ No specific company info found", "gray")
                            except Exception as research_error:
                                self.root.after(0, self.log, f"  ⚠ Company research failed: {str(research_error)}", "orange")

                    # Generate content
                    self.root.after(0, self.log, f"  Analyzing job and generating content...", "gray")

                    try:
                        outputs = self.generate_for_job(
                            client, model, combined_profile, job_data,
                            cv_template, cover_template, talking_template, company_info
                        )
                        print(f"DEBUG: Generated {len(outputs)} outputs")  # DEBUG
                    except Exception as api_error:
                        print(f"DEBUG: API error: {api_error}")  # DEBUG
                        self.root.after(0, self.log, f"  ✗ API Error: {str(api_error)}", "red")
                        import traceback
                        print(traceback.format_exc())  # DEBUG
                        self.root.after(0, self.log, f"  Details: {traceback.format_exc()}", "red")
                        continue

                    # Save outputs
                    base_name = os.path.splitext(job_filename)[0]

                    if not outputs:
                        self.root.after(0, self.log, f"  ⚠ No content generated", "orange")
                        continue

                    for content_type, content in outputs.items():
                        if content:
                            output_filename = f"{base_name}_{content_type}.txt"
                            output_path = os.path.join(self.current_output_folder, output_filename)

                            print(f"DEBUG: Saving {content_type} to {output_path}")  # DEBUG
                            try:
                                with open(output_path, 'w', encoding='utf-8') as f:
                                    f.write(content)
                                print(f"DEBUG: File saved successfully, size: {len(content)} chars")  # DEBUG
                                self.root.after(0, self.log, f"  ✓ Saved: {output_filename}", "green")
                            except Exception as save_error:
                                print(f"DEBUG: Save error: {save_error}")  # DEBUG
                                self.root.after(0, self.log, f"  ✗ Save Error: {str(save_error)}", "red")

                except Exception as e:
                    self.root.after(0, self.log, f"  ✗ Error processing job: {str(e)}", "red")
                    import traceback
                    self.root.after(0, self.log, f"  Full traceback: {traceback.format_exc()}", "red")

            # Done
            self.root.after(0, self.show_completion_summary)

        except Exception as e:
            error_msg = f"Generation error: {str(e)}"
            self.root.after(0, self.log, error_msg, "red")
            self.root.after(0, messagebox.showerror, "Error", error_msg)

        finally:
            self.root.after(0, self.generate_button.config, {"state": "normal"})
            self.root.after(0, self.stop_button.config, {"state": "disabled"})
            self.root.after(0, self.open_output_button.config, {"state": "normal"})
            self.processing = False

    def generate_for_job(self, client, model, profile, job_data, cv_template, cover_template, talking_template, company_info=None):
        """Generate customized content for one job using templates"""
        outputs = {}

        # Generate CV
        if cv_template:
            cv_prompt = self.fill_template(cv_template, profile, job_data, company_info)
            if cv_prompt:
                response = client.messages.create(
                    model=model,
                    max_tokens=4000,
                    messages=[{"role": "user", "content": cv_prompt}]
                )
                outputs['CV'] = response.content[0].text

        # Generate cover letter
        if cover_template:
            cover_prompt = self.fill_template(cover_template, profile, job_data, company_info)
            if cover_prompt:
                response = client.messages.create(
                    model=model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": cover_prompt}]
                )
                outputs['CoverLetter'] = response.content[0].text

        # Generate talking points
        if talking_template:
            talking_prompt = self.fill_template(talking_template, profile, job_data, company_info)
            if talking_prompt:
                response = client.messages.create(
                    model=model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": talking_prompt}]
                )
                outputs['TalkingPoints'] = response.content[0].text

        return outputs

    def show_completion_summary(self):
        """Show completion summary"""
        self.log("-" * 80, "gray")
        self.log("CV GENERATION COMPLETE!", "blue")
        self.log(f"Output folder: {self.current_output_folder}", "blue")
        self.update_status("✓ Generation complete!", "green")

        messagebox.showinfo(
            "Complete",
            f"CV generation complete!\n\nFiles saved to:\n{self.current_output_folder}"
        )

    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.progress_text.config(text="0 / 0 CVs generated")
        self.update_status("Ready to generate customized CVs", "green")

    def open_output_folder(self):
        """Open output folder"""
        if hasattr(self, 'current_output_folder') and os.path.exists(self.current_output_folder):
            system = platform.system()
            try:
                if system == "Windows":
                    os.startfile(self.current_output_folder)
                elif system == "Darwin":
                    subprocess.run(["open", self.current_output_folder])
                else:
                    subprocess.run(["xdg-open", self.current_output_folder])
            except:
                messagebox.showinfo("Folder Path", f"Output folder:\n{self.current_output_folder}")
        else:
            messagebox.showwarning("No Folder", "No output folder created yet")


def main():
    """Run the application"""
    root = tk.Tk()
    app = CVCustomizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

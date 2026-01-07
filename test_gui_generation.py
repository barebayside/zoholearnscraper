"""
Test the GUI generation logic directly without the GUI
"""

import json
import os
from anthropic import Anthropic
from datetime import datetime

# Configuration
API_KEY = "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"
JOB_FOLDER = r"C:\Users\edast\OneDrive\Desktop\Python Course\Scrape Project\batches\batch_2025-11-07_131234"
OUTPUT_FOLDER = r"C:\Users\edast\OneDrive\Desktop\test_batch"

# Simulate profile documents (add real paths if you have them)
PROFILE_DOCUMENTS = [
    # Add your profile document paths here, or we'll use sample text
]

# Sample profile if no documents provided
SAMPLE_PROFILE = """
John Doe
Email: john.doe@example.com
Phone: (123) 456-7890

PROFESSIONAL SUMMARY
Experienced professional with 5+ years in software development and project management.
Strong skills in Python, JavaScript, web development, team collaboration, and client relations.

WORK EXPERIENCE
Software Engineer | Tech Company | 2020-Present
- Developed web applications using Python and JavaScript
- Managed projects from inception to deployment
- Collaborated with cross-functional teams

EDUCATION
Bachelor of Computer Science | University | 2019

SKILLS
- Programming: Python, JavaScript, SQL
- Project Management
- Team Leadership
- Communication
"""

def read_document(filepath):
    """Read a document (simplified)"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return f"[Error reading {filepath}]"

def test_generation():
    print("="*80)
    print("GUI GENERATION LOGIC TEST")
    print("="*80)
    
    # Step 1: Initialize API
    print("\n1. Initializing Claude API...")
    try:
        client = Anthropic(api_key=API_KEY)
        print("   ✓ API initialized")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        return
    
    # Step 2: Load profile
    print("\n2. Loading profile documents...")
    if PROFILE_DOCUMENTS:
        profile_content = []
        for filepath in PROFILE_DOCUMENTS:
            content = read_document(filepath)
            profile_content.append(f"=== Document: {os.path.basename(filepath)} ===\n{content}")
        combined_profile = "\n\n".join(profile_content)
        print(f"   ✓ Loaded {len(PROFILE_DOCUMENTS)} document(s)")
    else:
        combined_profile = SAMPLE_PROFILE
        print("   ⚠ Using sample profile (no documents provided)")
    
    print(f"   Profile length: {len(combined_profile)} characters")
    
    # Step 3: Load job files
    print("\n3. Loading job files...")
    try:
        job_files = [os.path.join(JOB_FOLDER, f) for f in os.listdir(JOB_FOLDER) if f.endswith('.json')]
        print(f"   ✓ Found {len(job_files)} job file(s)")
        
        if not job_files:
            print("   ✗ No job files found!")
            return
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        return
    
    # Step 4: Create output folder
    print("\n4. Creating output folder...")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_folder = os.path.join(OUTPUT_FOLDER, f"batch_{timestamp}")
    try:
        os.makedirs(output_folder, exist_ok=True)
        print(f"   ✓ Created: {output_folder}")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        return
    
    # Step 5: Generate for first job
    print("\n5. Generating CV for first job...")
    job_file = job_files[0]
    job_filename = os.path.basename(job_file)
    print(f"   Processing: {job_filename}")
    
    try:
        # Load job data
        with open(job_file, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
        
        job_title = job_data.get('job_title', 'Unknown')
        company = job_data.get('company', 'Unknown')
        print(f"   Job: {job_title} at {company}")
        
        # Check if error in job data
        if 'error' in job_data:
            print(f"   ⚠ Job data has error: {job_data['error']}")
            return
        
        # Generate CV
        print("   Calling Claude API to generate CV...")
        
        cv_prompt = f"""You are an expert CV writer. I need you to create a customized CV/resume tailored for a specific job.

Here is my complete professional profile:

{combined_profile}

Here is the job I'm applying for:
- Job Title: {job_title}
- Company: {company}
- Job Requirements: {json.dumps(job_data.get('requirements', []), indent=2)}
- Required Skills: {json.dumps(job_data.get('skills', []), indent=2)}
- Description: {job_data.get('description', 'N/A')[:500]}

Please create a customized CV that highlights my most relevant experience for THIS specific job.
Format as plain text with clear sections. Keep it concise (2-3 paragraphs for this test)."""

        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            messages=[{"role": "user", "content": cv_prompt}]
        )
        
        cv_content = response.content[0].text
        print(f"   ✓ CV generated ({len(cv_content)} characters)")
        
        # Save to file
        base_name = os.path.splitext(job_filename)[0]
        output_filename = f"{base_name}_CV.txt"
        output_path = os.path.join(output_folder, output_filename)
        
        print(f"   Saving to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cv_content)
        
        print(f"   ✓ File saved!")
        
        # Verify file exists
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   ✓ Verified: File exists ({file_size} bytes)")
        else:
            print(f"   ✗ ERROR: File was not saved!")
        
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        import traceback
        print(traceback.format_exc())
        return
    
    # Success
    print("\n" + "="*80)
    print("✓ TEST COMPLETE!")
    print("="*80)
    print(f"\nOutput folder: {output_folder}")
    print("\nCV Preview:")
    print("-"*80)
    print(cv_content[:300] + "...")
    print("-"*80)
    
    # List files in output folder
    print(f"\nFiles in output folder:")
    for f in os.listdir(output_folder):
        fpath = os.path.join(output_folder, f)
        fsize = os.path.getsize(fpath)
        print(f"  - {f} ({fsize} bytes)")

if __name__ == "__main__":
    test_generation()

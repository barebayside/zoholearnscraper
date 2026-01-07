"""
Direct test script for CV generation (without GUI)
This will help diagnose the issue
"""

import json
import os
from anthropic import Anthropic

def test_cv_generation():
    """Test CV generation directly"""
    
    # ===== CONFIGURATION =====
    # Enter your API key here
    API_KEY = "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"  # Replace with your actual API key
    
    # Path to a job JSON file
    JOB_FILE = r"C:\Users\edast\OneDrive\Desktop\Python Course\Scrape Project\batches\batch_2025-11-07_131234\job_001_project_support_administrative_aussie_enviro_excava.json"
    
    # Path to a profile document (TXT file for simplicity)
    PROFILE_TEXT = """
John Doe
Software Engineer
5 years of experience in Python, JavaScript, and web development.
Strong skills in project management and team collaboration.
    """
    
    # ===== TEST =====
    print("="*80)
    print("DIRECT CV GENERATION TEST")
    print("="*80)
    
    # Step 1: Test API connection
    print("\n1. Testing API connection...")
    try:
        client = Anthropic(api_key=API_KEY)
        print("   ✓ API client initialized")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        print("\n   ERROR: Invalid API key or anthropic library issue")
        print("   SOLUTION: Make sure you've entered a valid API key above")
        return
    
    # Step 2: Test API call
    print("\n2. Testing API call...")
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'OK'"}]
        )
        print(f"   ✓ API working! Response: {response.content[0].text}")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        print("\n   ERROR: API call failed")
        print("   SOLUTION: Check your API key, internet connection, or API credits")
        return
    
    # Step 3: Load job data
    print("\n3. Loading job data...")
    try:
        if not os.path.exists(JOB_FILE):
            print(f"   ✗ Job file not found: {JOB_FILE}")
            print("   SOLUTION: Update JOB_FILE path in this script to point to a valid JSON file")
            return
            
        with open(JOB_FILE, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
        
        job_title = job_data.get('job_title', 'Unknown')
        company = job_data.get('company', 'Unknown')
        print(f"   ✓ Loaded job: {job_title} at {company}")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        return
    
    # Step 4: Generate CV
    print("\n4. Generating customized CV...")
    try:
        prompt = f"""You are an expert CV writer. Create a brief customized CV for this job.

My profile:
{PROFILE_TEXT}

Job:
- Title: {job_data.get('job_title', 'N/A')}
- Company: {job_data.get('company', 'N/A')}
- Description: {job_data.get('description', 'N/A')[:500]}

Write a brief 2-paragraph customized CV summary."""

        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        cv_content = response.content[0].text
        print(f"   ✓ CV generated ({len(cv_content)} characters)")
        
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        import traceback
        print(traceback.format_exc())
        return
    
    # Step 5: Save to file
    print("\n5. Saving to file...")
    try:
        output_file = "test_cv_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cv_content)
        
        output_path = os.path.abspath(output_file)
        print(f"   ✓ Saved to: {output_path}")
        
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        return
    
    # Success!
    print("\n" + "="*80)
    print("✓ SUCCESS! All tests passed.")
    print("="*80)
    print("\nGenerated CV preview:")
    print("-"*80)
    print(cv_content[:500] + "...")
    print("-"*80)
    print(f"\nFull output saved to: {output_path}")
    print("\nThe CV generation is working!")
    print("The issue is likely in the GUI threading or event handling.")


if __name__ == "__main__":
    test_cv_generation()

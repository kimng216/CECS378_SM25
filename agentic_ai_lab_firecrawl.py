import ollama
import requests
from fpdf import FPDF

# ===== CONFIGURATION =====
FIRECRAWL_API_KEY = 'fc-2f5d88a5251c404c8123da49496518f4'
FIRECRAWL_URL = 'https://api.firecrawl.dev/v1/scrape' 
MODEL_NAME = 'mistral'

# ===== DATA COLLECTION FROM WEB =====
def collect_data_from_url(url):
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {FIRECRAWL_API_KEY}'
    }
    json_data = {
        'url': url
    }
    response = requests.post(FIRECRAWL_URL, headers=headers, json=json_data)
    
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        try:
            print("Response content:", response.json())
        except Exception:
            print("Response content:", response.text)
        return None
    
    data = response.json()
    
    if not data.get('text', ''):
        print("Full API response:", data)

    return data.get('text') or data.get('data', {}).get('markdown', '')

# ===== PROCESS USING OFFLINE LLM =====
def process_with_llm(content):
    print("\nProcessing content with offline LLM...")
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{
            'role': 'user',
            'content': f"Please summarize and extract key actionable insights from the following content for a cybersecurity student:\n\n{content}"
        }]
    )
    return response['message']['content']

# ===== GENERATE PDF REPORT =====
def generate_pdf(content, filename="agentic_ai_summary.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    lines = content.split('\n')
    for line in lines:
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)
    print(f"PDF report generated: {filename}")

# ===== MAIN EXECUTION FLOW =====
def main():
    print("=== Agentic AI Lab: Firecrawl + Offline LLM + PDF Generator ===")
    url = input("Enter the URL to collect data from: ")
    try:
        scraped_text = collect_data_from_url(url)
        if not scraped_text:
            print("No content retrieved from the URL.")
            return
        summary = process_with_llm(scraped_text)
        print("\n--- LLM Processed Summary ---")
        print(summary)
        generate_pdf(summary)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

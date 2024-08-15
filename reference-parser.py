import PyPDF2
import re
from collections import defaultdict
import argparse
import logging
from tqdm import tqdm
import pandas as pd
from fuzzywuzzy import fuzz

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_text(text):
    """Clean and normalize text."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'([a-z])\.([A-Z])', r'\1. \2', text)  # Fix spacing after periods
    return text.strip()

def extract_references(pdf_path, start_pattern, end_pattern):
    """Extract references from PDF."""
    logging.info(f"Processing PDF: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ' '.join(page.extract_text() for page in tqdm(reader.pages, desc="Extracting text"))
    except Exception as e:
        logging.error(f"Error reading PDF: {e}")
        return None

    logging.debug(f"Total extracted text length: {len(text)}")
    logging.debug(f"First 500 characters of extracted text: {text[:500]}")

    # Try to find the references section
    match = re.search(f'{start_pattern}(.*?){end_pattern}', text, re.DOTALL | re.IGNORECASE)
    if not match:
        logging.warning(f"References section not found using patterns. Searching for alternative patterns...")
        # Try alternative patterns
        alt_start_patterns = [r"References", r"Bibliography", r"Works Cited"]
        alt_end_patterns = [r"Appendix", r"Index", r"End of document"]
        
        for s_pattern in alt_start_patterns:
            for e_pattern in alt_end_patterns:
                match = re.search(f'{s_pattern}(.*?){e_pattern}', text, re.DOTALL | re.IGNORECASE)
                if match:
                    logging.info(f"Found references using alternative patterns: {s_pattern} to {e_pattern}")
                    break
            if match:
                break
    
    if not match:
        logging.warning("References section not found. Returning entire text for manual inspection.")
        return text

    references_text = match.group(1).strip()
    logging.debug(f"Extracted references text length: {len(references_text)}")
    logging.debug(f"First 500 characters of references text: {references_text[:500]}")
    return references_text

def parse_references(references_text):
    """Parse references into structured format."""
    ref_dict = defaultdict(list)
    
    # Split by potential headings (all caps followed by year)
    sections = re.split(r'\n([A-Z][A-Z\s]+(?:\d{4})?)\n', references_text)
    
    if len(sections) < 2:
        logging.warning("No clear headings found. Treating entire text as one section.")
        sections = ["Unknown Heading", references_text]

    for i in range(0, len(sections), 2):
        heading = sections[i].strip() if i < len(sections) - 1 else "Unknown Heading"
        content = clean_text(sections[i+1] if i+1 < len(sections) else sections[i])
        
        # Parse individual references
        individual_refs = re.split(r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)?\s+(?:et\s+al\.?\s+)?(?:\d{4}[a-z]?))', content)
        for j in range(1, len(individual_refs), 2):
            ref_key = individual_refs[j].strip()
            ref_content = clean_text(individual_refs[j+1] if j+1 < len(individual_refs) else "")
            if ref_content:  # Only add if there's content
                ref_dict[heading].append((ref_key, ref_content))
    
    return ref_dict

# ... [rest of the script remains the same] ...

def main(pdf_path, output_file):
    start_pattern = r"References to studies included in this review"
    end_pattern = r"References to studies excluded from this review"
    
    references_text = extract_references(pdf_path, start_pattern, end_pattern)
    if references_text is None:
        return
    
    ref_dict = parse_references(references_text)
    
    if not ref_dict:
        logging.warning("No references parsed. Check the extracted text for manual processing.")
        with open("extracted_text.txt", "w", encoding="utf-8") as f:
            f.write(references_text)
        logging.info("Extracted text saved to 'extracted_text.txt' for manual inspection.")
        return

    df = analyze_references(ref_dict)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    logging.info(f"References saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and analyze references from a PDF.")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output", default="references.csv", help="Output CSV file name")
    args = parser.parse_args()

    main(args.pdf_path, args.output)
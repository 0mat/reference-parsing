import fitz  # PyMuPDF
import re
import os

def extract_references_section(text):
    start_idx = text.find("References to studies included in this review")
    if start_idx != -1:
        text = text[start_idx:]
        end_idx = text.find("References to studies excluded from this review")
        if end_idx != -1:
            text = text[:end_idx]
    return text

def count_bold_headings_and_blocks_for_csv(text):
    # Pattern to match any bold heading with a study name and year
    heading_pattern = r"([A-Za-z]+ \d{4})"
    headings = re.findall(heading_pattern, text)
    
    # Split text based on these headings to count the number of blocks under each heading
    text_blocks = re.split(heading_pattern, text)[1:]  # Skip the first split as it will be empty
    
    # Regex pattern to identify text blocks
    block_pattern = r"(\n\s*\n|[•\d\)\(]+\s+|(?<=\n)[A-Z][a-z]+\s+\d{4}|\*{3,})"  # Including "***" as a potential block separator
    
    reference_blocks = []
    for i in range(0, len(text_blocks), 2):
        reference = text_blocks[i].strip()
        
        # Apply the regex to count blocks more effectively
        block_count = len(re.findall(block_pattern, text_blocks[i + 1].strip())) + 1
        reference_blocks.append((reference, block_count))
    
    return reference_blocks

def process_pdf(input_file, writer):
    # Read the PDF and extract text
    doc = fitz.open(input_file)
    text = ""
    for page in doc:
        text += page.get_text()

    # Extract the references section
    references_text = extract_references_section(text)

    # Get the reference blocks with their counts
    reference_blocks = count_bold_headings_and_blocks_for_csv(references_text)

    # Get just the file name without the directory path
    file_name = os.path.basename(input_file)

    # Write to CSV
    for reference, count in reference_blocks:
        writer.writerow([file_name, reference, count])

import csv
import fitz  # PyMuPDF
import re
import sys

def extract_references_section(text):
    start_idx = text.find("References to studies included in this review")
    if start_idx != -1:
        text = text[start_idx:]
        end_idx = text.find("References to studies excluded from this review")
        if end_idx != -1:
            text = text[:end_idx]
    return text

def count_bold_headings_and_blocks_for_csv(text):
    heading_pattern = r"([A-Za-z]+ \d{4} \{published data only\})"
    headings = re.findall(heading_pattern, text)
    
    # Split text based on these headings to count the number of blocks under each heading
    text_blocks = re.split(heading_pattern, text)[1:]  # Skip the first split as it will be empty
    
    # Final detailed regex pattern
    block_pattern = r"(\n\s*\n|[•\d\)\(]+\s+|(?<=\n)[A-Z][a-z]+\s+\d{4}|\*{3,})"  # Including "***" as a potential block separator
    
    reference_blocks = []
    for i in range(0, len(text_blocks), 2):
        reference = text_blocks[i].strip()
        
        # Applying the final chunking regex to identify blocks more effectively
        block_count = len(re.findall(block_pattern, text_blocks[i + 1].strip())) + 1
        reference_blocks.append((reference, block_count))
    
    return reference_blocks

def process_pdf(input_file, output_file):
    # Read the PDF and extract text
    doc = fitz.open(input_file)
    text = ""
    for page in doc:
        text += page.get_text()

    # Extract the references section
    references_text = extract_references_section(text)

    # Get the reference blocks with their counts
    reference_blocks = count_bold_headings_and_blocks_for_csv(references_text)

    # Write to CSV
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['File Name', 'Bold Text', 'Number of References'])
        for reference, count in reference_blocks:
            writer.writerow([input_file, reference, count])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file_path> <output_file_path>")
    else:
        input_file_path = sys.argv[1]
        output_file_path = sys.argv[2]
        process_pdf(input_file_path, output_file_path)

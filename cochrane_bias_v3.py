import csv
import re

# Install the pdfminer.six library (if not already on computer)
#   Copy and paste the line below into your computer's terminal:
#       pip install pdfminer.six

from pdfminer.high_level import extract_text

def extract_references_and_save_to_csv(pdf_path, csv_path):
    # Extract the entire text from the PDF
    full_text = extract_text(pdf_path)
    
    # Normalize spaces to handle situations like "Referencestostudiesincludedinthisreview"
    normalized_text = re.sub(r'\s+', '', full_text)
    
    # Define the section boundaries
    start_term = "Referencestostudiesincludedinthisreview"
    end_term = "Referencestostudiesexcludedfromthisreview"
    
    # Extract the text between the start and end terms
    start_index = normalized_text.find(start_term)
    end_index = normalized_text.find(end_term, start_index)
    
    if start_index == -1 or end_index == -1:
        print("Could not find the specified sections in the document.")
        return
    
    # Extract references section
    references_section = normalized_text[start_index + len(start_term):end_index]
    
    # Split the references based on a common pattern (e.g., '\d+.\s' for numbered references)
    references = re.split(r'\d+\.\s', references_section)
    references = [ref.strip() for ref in references if ref.strip()]  # Clean and remove empty entries
    
    # Write the references to a CSV file
    with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Reference"])  # Header
        for reference in references:
            writer.writerow([reference])
    
    print(f"Extracted {len(references)} references and saved them to {csv_path}.")

# Use the function

#pdf_path- replace text in quotes with Cochrane pdf filepath
pdf_path = r"cochrane_files\10.1002_14651858.CD001233.pub4.pdf" 
csv_path = r"extracted_references.csv"
extract_references_and_save_to_csv(pdf_path, csv_path)

#Sample Cochrane pdf filepaths

    #Sample 1
    # pdf_path = r"cochrane_files\10.1002_14651858.CD001506.pub5.pdf"

    #Sample 2
    # pdf_path = r"cochrane_files\10.1002_14651858.CD001233.pub4.pdf"

  
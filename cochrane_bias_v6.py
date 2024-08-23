import csv
import re
from pdfminer.high_level import extract_text

def extract_references_and_save_to_csv(pdf_path, csv_path):
    # Extract the entire text from the PDF
    full_text = extract_text(pdf_path)
    
    # Normalize spaces to handle tight text
    # This line removes all whitespace characters (spaces, newlines, etc.) from the text, 
    # which can help in finding sections and patterns that might be disrupted by spacing.

    # Idea: We could split by newline between references, but newline is not recognized
    #  in the Cochrane PDF itself.
    #   How could we modify the line of code below to not remove all spaces?
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
    
    # Extract the references section
    references_section = normalized_text[start_index + len(start_term):end_index]
    
    # Pattern to find references ending with [] or ()
    pattern = r'.*?\[[A-Za-z0-9:]{10,}\](?!\.)|.*?\([A-Za-z0-9\s]{10,}\)\.'
    
    # Find all matches in the references section
    references = re.findall(pattern, references_section)
    
    # Write the references to a CSV file
    with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Reference"])  # Header
        for reference in references:
            writer.writerow([reference.strip()])  # Write each reference to its own row
    
    print(f"Extracted {len(references)} references and saved them to {csv_path}.")
    
    #Checking the format - seems all the references are
    # put together without spaces in between them.
    print(f"references_section: {references_section}.") 


# Use the function
pdf_path = r"cochrane_files\10.1002_14651858.CD001506.pub5.pdf"
csv_path = r"extracted_references.csv"
extract_references_and_save_to_csv(pdf_path, csv_path)

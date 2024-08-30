import fitz  # PyMuPDF
import csv
import re

print("*DEBUG PRINTING BEGINS*")

def extract_bold_sections_and_text(pdf_path):
    doc = fitz.open(pdf_path)
    bold_subsections = []
    current_subsection = None
    current_text = ""
    stop_extraction = False
    section_counter = 0  # Counter for tracking "References to" section occurrences

    # Regular expression to match the desired bold author_year heading patterns
    # Desired patterns:
    #   1. author name + 4-digit year (e.g., Smith 2000) 
    #   2. author name + 4-digit year + single character (e.g., Smith 2000a)
    #   3. author name + 4-digit year + all-caps abbreviation in parentheses (e.g., Smith 2000 (MIT)) 
    #   4. author surname (first part) + hyphen(-) + author surname (second part) + 4-digit year (e.g., Jones-Smith 2000) 
    #   5. author surname (first part) + space (' ') + author surname (second part) + space (' ') + author surname (third part) + 4-digit year (e.g., van der Waals 2000)

    # Undesired pattern:
    #   3-character string + 8-digit number (e.g., NCT01234567) 
    #   because these headings refer to clinical trials, which do not have a DOI or PMID. 
    pattern = re.compile(r'\b[A-Za-z-]+(?: [A-Za-z-]+)* \d{4}[a-z]?\b(?: \([A-Z\s]+\))?')
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            for line in block.get("lines", []):
                if stop_extraction:
                    break  # Stop extraction if the condition is met
                    
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    
                    
                    # Count occurrences of "References to"
                    if "References to" in text and 'bold' in span["font"].lower():
                        section_counter += 1
                        print(f"\nEncountered section: {text}, \'References to\' Count: {section_counter}\n")  # Debug print
                        if section_counter == 2:
                            stop_extraction = True
                            break
                    
                    # Check if the text is bold by analyzing font properties
                    if 'bold' in span["font"].lower() and pattern.match(text) and section_counter < 2:
                        print(f"Found bold subsection: {text}")  # Debug print
                        # If there's an ongoing subsection, store it
                        if current_subsection and current_text.strip():
                            print(f"Appending subsection: {current_subsection}")  # Debug print
                            bold_subsections.append((current_subsection, current_text.strip()))
                        # Start a new subsection
                        current_subsection = text
                        current_text = ""
                    elif current_subsection and section_counter < 2:
                        # Append the text to the current subsection
                        current_text += span["text"] + " "

    # Add the last subsection and text if applicable
    if current_subsection and current_text.strip():
        print(f"Appending last subsection: {current_subsection}")  # Debug print
        bold_subsections.append((current_subsection, current_text.strip()))

    return bold_subsections

def save_to_csv(bold_subsections, output_csv):
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['author_year', 'citation_chunk', 'reference_doi', 'reference_pmid']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for subsection, text in bold_subsections:
            print(f"Writing to CSV: {subsection}, {text[:30]}...")  # Debug print
            doi_matches = re.findall(r'\[DOI:(.*?)\]', text)
            pmid_matches = re.findall(r'\[PMID:(.*?)\]', text)
            writer.writerow({'author_year': subsection, 'citation_chunk': text, 'reference_doi': doi_matches, 'reference_pmid': pmid_matches})
  
    # Count the number of rows in the output CSV (excluding the header)
    with open(output_csv, 'r', encoding='utf-8') as csvfile:
        num_of_references = sum(1 for row in csvfile) - 1
    
    print("\n*DEBUG PRINTING ENDS*\n")
    print("*REFERENCE INFORMATION*\n")
    print(f"References saved to {output_csv}")
    print(f"There are {num_of_references} references in {cochrane_doi}.\n")

# Replace the filepath below with the filepath to the Cochrane file of interest
# Repeat for each Cochrane file of interest
pdf_path = r"cochrane_files\10.1002_14651858.CD001211.pub4.pdf"


# Extract the Cochrane DOI from pdf_path using regex
cochrane_doi = re.search(r'cochrane_files\\(.+?)\.pdf', pdf_path).group(1)

output_csv = f"{cochrane_doi}_references.csv"

bold_subsections = extract_bold_sections_and_text(pdf_path)
save_to_csv(bold_subsections, output_csv)
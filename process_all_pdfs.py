import os
import csv
from pdf_processing import process_pdf

def process_directory(directory_path, output_file):
    # Get the total number of PDF files in the directory
    pdf_files = [filename for filename in os.listdir(directory_path) if filename.endswith('.pdf')]
    total_files = len(pdf_files)

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['File Name', 'Bold Text', 'Number of References'])

        # Loop through each file and process it
        for idx, filename in enumerate(pdf_files, start=1):
            file_path = os.path.join(directory_path, filename)
            print(f"Processing file {idx}/{total_files}: {filename}...")  # Status update

            process_pdf(file_path, writer)
            
            print(f"Finished processing {filename} ({idx}/{total_files}).")  # Status update

    print(f"All {total_files} files processed. Results saved to {output_file}.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python process_all_pdfs.py <directory_path> <output_file_path>")
    else:
        directory_path = sys.argv[1]
        output_file_path = sys.argv[2]
        process_directory(directory_path, output_file_path)

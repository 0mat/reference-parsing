import os
import PyPDF2
from PyPDF2.errors import PdfReadError
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import argparse
import logging
from functools import partial


def setup_logging(log_level):
    """Set up logging configuration."""
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_pdf(pdf_path, max_pages=5):
    """
    Analyze a single PDF file and return its characteristics.
    
    Args:
    pdf_path (str): Path to the PDF file
    max_pages (int): Maximum number of pages to analyze per PDF
    
    Returns:
    dict: A dictionary containing the analysis results
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            
            total_text = 0
            total_images = 0
            has_text_content = False
            
            for page_num in range(min(num_pages, max_pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                total_text += len(text.strip())
                
                if len(text.strip()) > 10:
                    has_text_content = True
                
                if '/XObject' in page['/Resources']:
                    xObject = page['/Resources']['/XObject'].get_object()
                    if xObject:
                        total_images += sum(1 for obj in xObject if xObject[obj]['/Subtype'] == '/Image')
            
            text_to_page_ratio = total_text / num_pages
            
            pdf_type = "Text-based" if text_to_page_ratio > 100 and has_text_content else \
                       "Image-based" if total_images > 0 and text_to_page_ratio < 50 else "Hybrid"
            
            return {
                "File Name": os.path.basename(pdf_path),
                "Pages": num_pages,
                "Type": pdf_type,
                "Avg Text/Page": round(text_to_page_ratio, 2),
                "Images": total_images,
                "Searchable": "Yes" if has_text_content else "No",
                "File Size (KB)": round(os.path.getsize(pdf_path) / 1024, 2)
            }
    
    except PdfReadError:
        logging.error(f"Failed to read PDF: {pdf_path}")
        return {"File Name": os.path.basename(pdf_path), "Error": "Failed to read PDF"}
    except Exception as e:
        logging.error(f"Error processing {pdf_path}: {str(e)}")
        return {"File Name": os.path.basename(pdf_path), "Error": str(e)}

def analyze_directory(directory_path, max_pages=5):
    """
    Analyze all PDF files in a directory using multi-threading.
    
    Args:
    directory_path (str): Path to the directory containing PDF files
    max_pages (int): Maximum number of pages to analyze per PDF
    
    Returns:
    pd.DataFrame: A DataFrame containing the analysis results for all PDFs
    """
    pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
    
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        analyze_pdf_partial = partial(analyze_pdf, max_pages=max_pages)
        future_to_pdf = {executor.submit(analyze_pdf_partial, os.path.join(directory_path, pdf)): pdf for pdf in pdf_files}
        
        results = []
        for future in tqdm(as_completed(future_to_pdf), total=len(pdf_files), desc="Analyzing PDFs"):
            results.append(future.result())
    
    return pd.DataFrame(results)

def generate_summary(df):
    """Generate and print summary statistics."""
    print("\nAnalysis Summary:")
    print(df.to_string(index=False))
    
    print("\nOverall Statistics:")
    print(f"Total PDFs analyzed: {len(df)}")
    print(f"Text-based PDFs: {df['Type'].value_counts().get('Text-based', 0)}")
    print(f"Image-based PDFs: {df['Type'].value_counts().get('Image-based', 0)}")
    print(f"Hybrid PDFs: {df['Type'].value_counts().get('Hybrid', 0)}")
    print(f"Searchable PDFs: {df['Searchable'].value_counts().get('Yes', 0)}")
    print(f"Non-searchable PDFs: {df['Searchable'].value_counts().get('No', 0)}")
    print(f"Average file size: {df['File Size (KB)'].mean():.2f} KB")
    
    # Check if 'Error' column exists before trying to access it
    if 'Error' in df.columns:
        print(f"PDFs with errors: {df['Error'].notna().sum()}")
    else:
        print("PDFs with errors: 0")

def main():
    parser = argparse.ArgumentParser(description="Analyze PDF files in a directory.")
    parser.add_argument("directory", help="Directory containing PDF files")
    parser.add_argument("--output", default="pdf_imageanalysis_summary.csv", help="Output CSV file name")
    parser.add_argument("--max-pages", type=int, default=5, help="Maximum number of pages to analyze per PDF")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the logging level")
    args = parser.parse_args()

    setup_logging(args.log_level)

    logging.info(f"Analyzing PDFs in directory: {args.directory}")
    df = analyze_directory(args.directory, args.max_pages)
    
    df_sorted = df.sort_values('File Name')
    generate_summary(df_sorted)
    
    df_sorted.to_csv(args.output, index=False)
    logging.info(f"Detailed analysis saved to '{args.output}'")

    return 0

if __name__ == "__main__":
    exit(main())
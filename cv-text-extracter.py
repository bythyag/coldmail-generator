import os
# from PyPDF2 import PdfReader # Removed PyPDF2
import fitz  # PyMuPDF # Added PyMuPDF
import sys

def extract_text_from_pdf(pdf_path):
    """
    Extracts text content from a given PDF file using PyMuPDF.

    Args:
        pdf_path (str): The full path to the input PDF file.

    Returns:
        str: The extracted text content, or None if an error occurs.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at '{pdf_path}'")
        return None

    print(f"Reading PDF: {pdf_path}")
    text = ""
    doc = None # Initialize doc to None
    try:
        doc = fitz.open(pdf_path) # Open PDF with fitz
        num_pages = doc.page_count # Get page count
        print(f"Found {num_pages} page(s).")
        for i, page in enumerate(doc.pages()): # Iterate through pages
            page_text = page.get_text("text") # Extract text from page
            if page_text:
                text += page_text + "\n" # Add a newline between pages
            else:
                print(f"Warning: No text found on page {i+1}")
        print("Finished extracting text.")
        return text
    except Exception as e:
        print(f"Error reading PDF file '{pdf_path}' with PyMuPDF: {e}")
        return None
    finally:
        if doc:
            doc.close() # Ensure the document is closed

def save_text_to_file(text, output_path):
    """
    Saves the given text content to a specified file path.

    Args:
        text (str): The text content to save.
        output_path (str): The full path for the output text file.
    """
    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            print(f"Creating output directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)

        print(f"Saving extracted text to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(text)
        print("Successfully saved text file.")
    except Exception as e:
        print(f"Error saving text to file '{output_path}': {e}")

if __name__ == "__main__":
    # --- Configuration ---
    # Get the absolute path of the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define directories relative to the script's location
    input_pdf_directory = os.path.join(script_dir, "cv-pdf")
    output_text_directory = os.path.join(script_dir, "cv-texts")

    # You can specify the PDF filename directly or get it from arguments
    if len(sys.argv) > 1:
        pdf_filename = sys.argv[1]
        print(f"Using PDF filename from command line argument: {pdf_filename}")
    else:
        # Default PDF filename if no argument is provided
        pdf_filename = "Thyag_Raj.pdf"
        print(f"Using default PDF filename: {pdf_filename}")

    # Construct the full absolute path to the input PDF
    input_pdf_path = os.path.join(input_pdf_directory, pdf_filename)

    # Create the output filename based on the input PDF filename
    base_filename = os.path.splitext(pdf_filename)[0]
    output_txt_filename = f"{base_filename}_extracted.txt"
    # Construct the full absolute path for the output text file
    output_txt_path = os.path.join(output_text_directory, output_txt_filename)
    # --- End Configuration ---

    # Extract text from the PDF
    extracted_content = extract_text_from_pdf(input_pdf_path)

    # Save the extracted text if extraction was successful
    if extracted_content is not None:
        save_text_to_file(extracted_content, output_txt_path)
    else:
        print("Text extraction failed. No text file created.")
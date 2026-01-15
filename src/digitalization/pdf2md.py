import sys
import argparse
from pathlib import Path
import pymupdf4llm

# Adjust import path to allow importing from src if run as script
# We add the project root to sys.path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.digitalization.utils import get_next_id, increment_id, update_doc_info, check_doc_exists

OUTPUT_DIR = Path("doc") / "subjects" / "markdown"

def convert_pdf_to_md(pdf_path: str):
    """
    Converts a PDF file to Markdown using pymupdf4llm and saves it
    to doc/subjects/markdown/[filename] [ID].md.
    Returns:
        tuple: (output_path (Path or None), is_success (bool))
    """
    input_path = Path(pdf_path).resolve()
    
    if not input_path.exists():
        print(f"Error: File not found at {input_path}")
        return None, False
    
    if input_path.suffix.lower() != '.pdf':
        print(f"Error: The file {input_path.name} is not a PDF.")
        return None, False

    if check_doc_exists(input_path.name):
        print(f"Skipping conversion: '{input_path.name}' already exists in registry.")
        return None, False

    doc_id = get_next_id()
    # Format: [ID]_filename.md
    output_filename = f"[{doc_id}]_{input_path.stem}.md"
    output_path = OUTPUT_DIR / output_filename

    print(f"Converting '{input_path.name}' to Markdown with ID [{doc_id}]...")
    
    try:
        # Create output directory if it doesn't exist
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Convert to markdown
        md_text = pymupdf4llm.to_markdown(str(input_path))
        
        # Save to file
        output_path.write_text(md_text, encoding='utf-8')
        print(f"Successfully saved to: {output_path}")
        
        # Update registry
        update_doc_info(doc_id, input_path, output_path)

        # Increment ID after successful save
        increment_id()
        
        return output_path, True
        
    except Exception as e:
        print(f"An error occurred during conversion: {e}")
        return None, False

if __name__ == "__main__":
    pdf_path = "doc/subjects/Grade 12 Physics Unit 1 2 en.pdf"
    
    converted_path, is_success = convert_pdf_to_md(pdf_path)
    print(f"Conversion Status: {'Success' if is_success else 'Fail'}")
    if is_success:
        print(f"Output File: {converted_path}")

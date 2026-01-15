from pathlib import Path
from datetime import datetime
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOC_ID_PATH = PROJECT_ROOT / "config" / "DOC_ID.txt"
DOC_INFO_PATH = PROJECT_ROOT / "config" / "doc_info.yaml"

SUBJECTS = ['physics', 'chemistry', 'maths']

def get_next_id() -> int:
    """Reads the current ID from the config file."""
    
    try:
        content = DOC_ID_PATH.read_text().strip()
        return int(content)
    except ValueError:
        return 1

def increment_id() -> None:
    """Increments the ID in the config file by 1."""
    current_id = get_next_id()
    new_id = current_id + 1
    
    # Ensure directory exists though it should
    DOC_ID_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    DOC_ID_PATH.write_text(str(new_id))

def detect_subject(filename: str) -> str:
    """
    Detects the subject from the filename. 
    Defaults to 'other' if no subject is found.
    """
    fname_lower = filename.lower()
    for subject in SUBJECTS:
        if subject in fname_lower:
            return subject
    return 'other'

def update_doc_info(doc_id: int, pdf_path: Path, md_path: Path) -> None:
    """Updates the doc_info.yaml file with the new document details."""
    
    # Initialize default structure if file doesn't exist or is empty
    data = {}
    if DOC_INFO_PATH.exists():
        try:
            with open(DOC_INFO_PATH, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not read doc_info.yaml: {e}")
            data = {}
            
    subject_key = detect_subject(pdf_path.stem)
    
    if subject_key not in data:
        data[subject_key] = []
        
    # Create new entry
    new_entry = {
        'doc_id': doc_id,
        'doc_name': pdf_path.name,
        'doc_path': str(pdf_path),
        'md_path': str(md_path),
        'converted_date': datetime.now().isoformat()
    }
    
    # Append to list
    if data[subject_key] is None:
        data[subject_key] = "Uncategorized"
        
    data[subject_key].append(new_entry)
    
    # Write back
    try:
        with open(DOC_INFO_PATH, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
        print(f"Updated doc_info.yaml with Doc ID {doc_id} under subject '{subject_key}'")
    except Exception as e:
        print(f"Error writing to doc_info.yaml: {e}")

def check_doc_exists(doc_name: str) -> bool:
    """
    Checks if a document with the given name already exists in doc_info.yaml.
    """
    if not DOC_INFO_PATH.exists():
        return False
        
    try:
        with open(DOC_INFO_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
            
        subject_key = detect_subject(doc_name)
        subject_list = data.get(subject_key, [])
        if not subject_list:
            return False
            
        for entry in subject_list:
            if isinstance(entry, dict) and entry.get('doc_name') == doc_name:
                return True
                
        return False
        
    except Exception as e:
        print(f"Warning: Could not check for existing doc: {e}")
        return False

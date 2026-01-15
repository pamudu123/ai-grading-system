"""
Context Retriever Tool - Fetches relevant content from subject markdown files.
"""
from pathlib import Path
import yaml

from ..config import DOC_INFO_PATH, PROJECT_ROOT


def get_subject_documents(subject: str) -> list[dict]:
    """
    Read doc_info.yaml and return document entries for the specified subject.
    
    Args:
        subject: The subject name (e.g., 'physics', 'chemistry', 'maths')
    
    Returns:
        List of document dictionaries with doc_id, doc_name, doc_path, md_path
    """
    if not DOC_INFO_PATH.exists():
        print(f"Warning: doc_info.yaml not found at {DOC_INFO_PATH}")
        return []
    
    with open(DOC_INFO_PATH, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    
    subject_lower = subject.lower()
    documents = data.get(subject_lower, [])
    
    if not documents:
        print(f"No documents found for subject: {subject}")
        return []
    
    return documents


def load_markdown_content(md_path: str) -> str:
    """
    Load and return the content of a markdown file.
    
    Args:
        md_path: Path to the markdown file (can be relative or absolute)
    
    Returns:
        The content of the markdown file as a string
    """
    # Handle relative paths
    path = Path(md_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / md_path
    
    if not path.exists():
        print(f"Warning: Markdown file not found at {path}")
        return ""
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return content


def retrieve_context(subject: str, max_chars: int = 15000) -> str:
    """
    Main function to retrieve relevant context for question generation.
    
    This function:
    1. Gets all documents for the subject from doc_info.yaml
    2. Loads the markdown content from those documents
    3. Returns concatenated content (limited by max_chars)
    
    Args:
        subject: The subject to retrieve context for
        max_chars: Maximum characters to return (to fit in LLM context)
    
    Returns:
        Concatenated markdown content from subject documents
    """
    documents = get_subject_documents(subject)
    
    if not documents:
        return f"No content available for subject: {subject}"
    
    all_content = []
    total_chars = 0
    
    for doc in documents:
        md_path = doc.get('md_path', '')
        if not md_path:
            continue
        
        content = load_markdown_content(md_path)
        if not content:
            continue
        
        # Check if adding this content would exceed the limit
        if total_chars + len(content) > max_chars:
            # Add partial content if possible
            remaining = max_chars - total_chars
            if remaining > 500:  # Only add if there's meaningful space left
                all_content.append(content[:remaining])
            break
        
        all_content.append(content)
        total_chars += len(content)
    
    if not all_content:
        return f"Could not load content for subject: {subject}"
    
    return "\n\n---\n\n".join(all_content)


def get_available_subjects() -> list[str]:
    """
    Get list of all available subjects from doc_info.yaml.
    
    Returns:
        List of subject names
    """
    if not DOC_INFO_PATH.exists():
        return []
    
    with open(DOC_INFO_PATH, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    
    return list(data.keys())

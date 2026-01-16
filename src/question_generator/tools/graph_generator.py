"""
Graph Generator Tool - Creates graphs for mathematical expressions.

Uses matplotlib to generate graphs for equations like:
- Linear: y = mx + c
- Quadratic: y = ax² + bx + c
- Custom expressions
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving files



# ============================================================================
# DYNAMIC GRAPH GENERATION TOOL
# ============================================================================

def execute_graph_code(code: str, output_path: str) -> str:
    """
    Execute Python code to generate a graph.
    
    Args:
        code: Python code using matplotlib (must save to `output_path` or use `plt.savefig(output_path)`)
        output_path: The absolute path where the image should be saved
    
    Returns:
        Path to the saved image, or raises Exception on failure
    """
    # Create a safe-ish dictionary for execution
    # We allow numpy and matplotlib
    local_scope = {
        "np": np,
        "plt": plt,
        "output_path": output_path
    }
    
    # Wrap code to ensure it uses the provided output_path if it hardcodes 'filename.png'
    # Actually, best to instruct LLM to use the variable `output_path`
    
    try:
        # 1. Ensure the directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 2. Execute the code
        exec(code, globals(), local_scope)
        
        # 3. Check if file was created
        if not Path(output_path).exists():
            # Attempt to save if the user code just plotted but didn't save
            # This handles cases where LLM forgets plt.savefig(output_path)
            if plt.get_fignums():
                plt.savefig(output_path, dpi=150, bbox_inches='tight')
                plt.close()
            else:
                raise FileNotFoundError(f"Code executed but {output_path} was not created and no figure was active.")
        
        # Ensure cleanup
        plt.close('all')
        
        return str(output_path)
        
    except Exception as e:
        plt.close('all')
        raise RuntimeError(f"Failed to execute graph code: {e}")

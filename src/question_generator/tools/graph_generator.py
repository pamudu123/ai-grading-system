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


def generate_linear_graph(
    m: float, 
    c: float, 
    output_path: str,
    x_range: tuple[float, float] = (-10, 10),
    title: str | None = None
) -> str:
    """
    Generate a graph for linear equation y = mx + c.
    
    Args:
        m: Slope of the line
        c: Y-intercept
        output_path: Path to save the PNG file
        x_range: Tuple of (x_min, x_max)
        title: Optional title for the graph
    
    Returns:
        Path to the saved graph image
    """
    x = np.linspace(x_range[0], x_range[1], 100)
    y = m * x + c
    
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, 'b-', linewidth=2)
    plt.axhline(y=0, color='k', linewidth=0.5)
    plt.axvline(x=0, color='k', linewidth=0.5)
    plt.grid(True, alpha=0.3)
    plt.xlabel('x')
    plt.ylabel('y')
    
    if title:
        plt.title(title)
    else:
        sign = '+' if c >= 0 else ''
        plt.title(f'y = {m}x {sign} {c}')
    
    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return str(output_file)


def generate_quadratic_graph(
    a: float, 
    b: float, 
    c: float, 
    output_path: str,
    x_range: tuple[float, float] = (-10, 10),
    title: str | None = None
) -> str:
    """
    Generate a graph for quadratic equation y = ax² + bx + c.
    
    Args:
        a: Coefficient of x²
        b: Coefficient of x
        c: Constant term
        output_path: Path to save the PNG file
        x_range: Tuple of (x_min, x_max)
        title: Optional title for the graph
    
    Returns:
        Path to the saved graph image
    """
    x = np.linspace(x_range[0], x_range[1], 200)
    y = a * x**2 + b * x + c
    
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, 'b-', linewidth=2)
    plt.axhline(y=0, color='k', linewidth=0.5)
    plt.axvline(x=0, color='k', linewidth=0.5)
    plt.grid(True, alpha=0.3)
    plt.xlabel('x')
    plt.ylabel('y')
    
    if title:
        plt.title(title)
    else:
        # Format equation string
        terms = []
        if a != 0:
            terms.append(f'{a}x²')
        if b != 0:
            sign = '+' if b > 0 else ''
            terms.append(f'{sign} {b}x')
        if c != 0:
            sign = '+' if c > 0 else ''
            terms.append(f'{sign} {c}')
        plt.title(f'y = {" ".join(terms)}')
    
    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return str(output_file)


def generate_custom_graph(
    expression_func,
    output_path: str,
    x_range: tuple[float, float] = (-10, 10),
    title: str = "Graph",
    x_label: str = "x",
    y_label: str = "y"
) -> str:
    """
    Generate a graph for a custom mathematical function.
    
    Args:
        expression_func: A callable that takes x (numpy array) and returns y
        output_path: Path to save the PNG file
        x_range: Tuple of (x_min, x_max)
        title: Title for the graph
        x_label: Label for x-axis
        y_label: Label for y-axis
    
    Returns:
        Path to the saved graph image
    """
    x = np.linspace(x_range[0], x_range[1], 200)
    y = expression_func(x)
    
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, 'b-', linewidth=2)
    plt.axhline(y=0, color='k', linewidth=0.5)
    plt.axvline(x=0, color='k', linewidth=0.5)
    plt.grid(True, alpha=0.3)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    
    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return str(output_file)


def generate_multiple_graphs(
    expressions: list[dict],
    output_path: str,
    x_range: tuple[float, float] = (-10, 10),
    title: str = "Comparison Graph",
    legend_labels: list[str] | None = None
) -> str:
    """
    Generate a graph with multiple functions plotted together.
    Useful for MCQ options showing different graphs.
    
    Args:
        expressions: List of dicts with 'type' and coefficients
                    e.g., [{'type': 'linear', 'm': 2, 'c': 1}, 
                           {'type': 'quadratic', 'a': 1, 'b': 0, 'c': 0}]
        output_path: Path to save the PNG file
        x_range: Tuple of (x_min, x_max)
        title: Title for the graph
        legend_labels: Optional list of labels for each curve
    
    Returns:
        Path to the saved graph image
    """
    colors = ['b', 'r', 'g', 'm', 'c', 'orange']
    x = np.linspace(x_range[0], x_range[1], 200)
    
    plt.figure(figsize=(10, 8))
    
    for i, expr in enumerate(expressions):
        color = colors[i % len(colors)]
        
        if expr['type'] == 'linear':
            m, c = expr.get('m', 1), expr.get('c', 0)
            y = m * x + c
            label = legend_labels[i] if legend_labels else f'y = {m}x + {c}'
        elif expr['type'] == 'quadratic':
            a = expr.get('a', 1)
            b = expr.get('b', 0)
            c = expr.get('c', 0)
            y = a * x**2 + b * x + c
            label = legend_labels[i] if legend_labels else f'y = {a}x² + {b}x + {c}'
        else:
            continue
        
        plt.plot(x, y, color=color, linewidth=2, label=label)
    
    plt.axhline(y=0, color='k', linewidth=0.5)
    plt.axvline(x=0, color='k', linewidth=0.5)
    plt.grid(True, alpha=0.3)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title(title)
    plt.legend()
    
    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return str(output_file)


# ============================================================================
# COMMENTED TOOLS (AS REQUESTED BY USER - DO NOT UNCOMMENT)
# ============================================================================

# # Python Interpreter Tool (COMMENTED - DO NOT USE)
# def python_interpreter_tool(code: str) -> str:
#     """
#     Execute Python code dynamically.
#     
#     DISABLED BY REQUIREMENT - This tool is intentionally commented out.
#     Graph generation is done directly via matplotlib functions above.
#     """
#     # WARNING: Executing arbitrary code is dangerous
#     # This tool is disabled as per user requirements
#     pass

# # Calculator Tool (COMMENTED - DO NOT USE)
# def calculator_tool(expression: str) -> float:
#     """
#     Calculate mathematical expressions.
#     
#     DISABLED BY REQUIREMENT - This tool is intentionally commented out.
#     Mathematical calculations should be done within the LLM's reasoning.
#     """
#     # This tool is disabled as per user requirements
#     pass

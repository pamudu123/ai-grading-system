"""
Configuration constants for the Question Generator system.
"""
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

# ============================================================================
# API Configuration
# ============================================================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "google/gemini-2.0-flash-001"

# ============================================================================
# Project Paths
# ============================================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DOC_INFO_PATH = CONFIG_DIR / "doc_info.yaml"
OUTPUT_DIR = PROJECT_ROOT / "output" / "questions"

# ============================================================================
# Question Generator Constants
# ============================================================================
DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

QUESTION_TYPES = ["MCQ", "Short Answer", "Long Answer"]

SUBJECTS = ["physics", "chemistry", "maths"]

DEFAULT_NUM_OPTIONS = 4
MIN_OPTIONS = 2
MAX_OPTIONS = 6

# ============================================================================
# Marking Scheme (Long Answer)
# ============================================================================
TOTAL_MARKS = 100

# ============================================================================
# LLM Configuration
# ============================================================================
MAX_RETRIES = 3
TEMPERATURE = 0.7
MAX_TOKENS = 4096

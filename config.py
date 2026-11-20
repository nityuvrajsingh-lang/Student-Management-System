"""
config.py - Central configuration for the Student Management System.

Every "magic number" or file path used by the project lives here, so that
changing a rule (for example the grading scale) needs an edit in ONE place.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# File locations (relative to this file, so the program works from any folder)
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORT_DIR = BASE_DIR / "exports"
STUDENTS_FILE = DATA_DIR / "students.json"          # live database
SAMPLE_FILE = DATA_DIR / "sample_students.json"     # demo data (never modified)

# ---------------------------------------------------------------------------
# Student ID format:  STU001, STU002, ...
# ---------------------------------------------------------------------------
ID_PREFIX = "STU"
ID_DIGITS = 3

# ---------------------------------------------------------------------------
# Marks and grading
# Marks are the TOTAL out of MAX_MARKS (for example 5 subjects x 100 = 500).
# ---------------------------------------------------------------------------
MAX_MARKS = 500
PASS_PERCENTAGE = 40.0

# (minimum percentage, grade) - checked from the top, so keep highest first.
GRADE_SCALE = [
    (90, "A+"),
    (80, "A"),
    (70, "B+"),
    (60, "B"),
    (50, "C"),
    (40, "D"),
    (0, "F"),
]

# ---------------------------------------------------------------------------
# Validation limits
# ---------------------------------------------------------------------------
DEPARTMENTS = ["CSE", "IT", "AIML", "ECE", "EEE", "ME", "CE"]
MIN_AGE, MAX_AGE = 16, 60
MIN_SEMESTER, MAX_SEMESTER = 1, 8

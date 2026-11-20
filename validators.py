"""
validators.py - Input validation helpers.

Every validate_* function follows the same contract:
    * it receives a raw value (usually text typed by the user),
    * it returns the CLEANED value (right type, trimmed, normalised),
    * it raises ValueError with a friendly message when the value is invalid.

Because they all behave the same way, the menu code and the data-loading
code can reuse them without special cases.
"""

import math
import re

from config import (
    DEPARTMENTS,
    ID_DIGITS,
    ID_PREFIX,
    MAX_AGE,
    MAX_MARKS,
    MAX_SEMESTER,
    MIN_AGE,
    MIN_SEMESTER,
)

# 2-50 characters, starts with a letter, then letters / spaces / . ' -
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z .'-]{1,49}$")
# Simple, practical e-mail check:  local-part @ domain . extension
EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$"
)
ID_PATTERN = re.compile(rf"^{ID_PREFIX}(\d+)$", re.IGNORECASE)

REQUIRED_FIELDS = ("id", "name", "age", "email", "department", "semester", "marks")


def _to_int(value, label):
    """Convert to int or raise a friendly ValueError (booleans are rejected)."""
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a whole number.")
    try:
        return int(str(value).strip())
    except ValueError:
        raise ValueError(f"{label} must be a whole number (digits only).") from None


def validate_name(value):
    """Collapse extra spaces, check the characters, and return Title Case."""
    name = " ".join(str(value).split())
    if not NAME_PATTERN.match(name):
        raise ValueError(
            "Name must be 2-50 characters, start with a letter and contain only "
            "letters, spaces, '.', apostrophes or '-'."
        )
    return name.title()


def validate_age(value):
    age = _to_int(value, "Age")
    if not MIN_AGE <= age <= MAX_AGE:
        raise ValueError(f"Age must be between {MIN_AGE} and {MAX_AGE}.")
    return age


def validate_email(value):
    email = str(value).strip().lower()
    if len(email) > 100 or not EMAIL_PATTERN.match(email):
        raise ValueError("Enter a valid e-mail address, for example name@example.com.")
    return email


def validate_department(value):
    department = str(value).strip().upper()
    if department not in DEPARTMENTS:
        raise ValueError("Department must be one of: " + ", ".join(DEPARTMENTS) + ".")
    return department


def validate_semester(value):
    semester = _to_int(value, "Semester")
    if not MIN_SEMESTER <= semester <= MAX_SEMESTER:
        raise ValueError(f"Semester must be between {MIN_SEMESTER} and {MAX_SEMESTER}.")
    return semester


def validate_marks(value):
    if isinstance(value, bool):
        raise ValueError("Marks must be a number.")
    try:
        marks = float(str(value).strip())
    except ValueError:
        raise ValueError("Marks must be a number, for example 432 or 432.5.") from None
    if not math.isfinite(marks):          # rejects 'nan' and 'inf'
        raise ValueError("Marks must be a valid number.")
    if not 0 <= marks <= MAX_MARKS:
        raise ValueError(f"Marks must be between 0 and {MAX_MARKS}.")
    return round(marks, 2)


def validate_student_id(value):
    """
    Accept 'STU001', 'stu1' or just '1' and return the standard form 'STU001'.
    """
    text = str(value).strip()
    if text.isdigit():
        number = int(text)
    else:
        match = ID_PATTERN.match(text)
        if not match:
            raise ValueError(f"Student ID must look like {ID_PREFIX}001 (or just the number 1).")
        number = int(match.group(1))
    return f"{ID_PREFIX}{number:0{ID_DIGITS}d}"


def validate_search_text(value):
    """Search text must not be empty (spaces are tidied up)."""
    text = " ".join(str(value).split())
    if not text:
        raise ValueError("Search text cannot be empty.")
    if len(text) > 50:
        raise ValueError("Search text is too long (maximum 50 characters).")
    return text


def validate_student_record(record):
    """
    Validate a whole student dictionary (used when loading the JSON file).
    Returns a cleaned copy or raises ValueError.
    """
    if not isinstance(record, dict):
        raise ValueError("each student record must be a JSON object.")
    missing = [field for field in REQUIRED_FIELDS if field not in record]
    if missing:
        raise ValueError("missing field(s): " + ", ".join(missing) + ".")
    return {
        "id": validate_student_id(record["id"]),
        "name": validate_name(record["name"]),
        "age": validate_age(record["age"]),
        "email": validate_email(record["email"]),
        "department": validate_department(record["department"]),
        "semester": validate_semester(record["semester"]),
        "marks": validate_marks(record["marks"]),
    }

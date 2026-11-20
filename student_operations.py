"""
student_operations.py - The core "business logic" of the application.

Add, search, update, delete, sort, and the percentage / grade calculations.
These functions work on a plain Python list of dictionaries and never print
or ask for input, which makes them easy to test and reuse.
"""

import validators
from config import GRADE_SCALE, ID_DIGITS, ID_PREFIX, MAX_MARKS, PASS_PERCENTAGE


class StudentNotFoundError(Exception):
    """Raised when no student with the requested ID exists."""


# Which validator checks which field (used by add and update).
FIELD_VALIDATORS = {
    "name": validators.validate_name,
    "age": validators.validate_age,
    "email": validators.validate_email,
    "department": validators.validate_department,
    "semester": validators.validate_semester,
    "marks": validators.validate_marks,
}


# ---------------------------------------------------------------------------
# Calculations
# ---------------------------------------------------------------------------
def calculate_percentage(marks):
    """Percentage = marks obtained / maximum marks x 100 (2 decimal places)."""
    return round(marks / MAX_MARKS * 100, 2)


def calculate_grade(percentage):
    """Return the grade for a percentage using the scale defined in config.py."""
    for minimum, grade in GRADE_SCALE:
        if percentage >= minimum:
            return grade
    return GRADE_SCALE[-1][1]


def get_result(percentage):
    """PASS when the percentage reaches the pass mark, otherwise FAIL."""
    return "PASS" if percentage >= PASS_PERCENTAGE else "FAIL"


def with_performance(student):
    """
    Return a COPY of the student with percentage, grade and result added.

    These three values are derived from marks, so they are calculated when
    needed instead of being stored (no risk of them going out of date).
    """
    percentage = calculate_percentage(student["marks"])
    enriched = dict(student)
    enriched["percentage"] = percentage
    enriched["grade"] = calculate_grade(percentage)
    enriched["result"] = get_result(percentage)
    return enriched


# ---------------------------------------------------------------------------
# ID helpers
# ---------------------------------------------------------------------------
def id_number(student_id):
    """'STU012' -> 12  (used for numeric ID generation and sorting)."""
    match = validators.ID_PATTERN.match(student_id)
    return int(match.group(1)) if match else 0


def generate_student_id(students):
    """Next ID = highest existing number + 1, so IDs never clash after a delete."""
    highest = max((id_number(s["id"]) for s in students), default=0)
    return f"{ID_PREFIX}{highest + 1:0{ID_DIGITS}d}"


def ensure_email_unique(students, email, ignore_id=None):
    """Raise ValueError if another student already uses this e-mail."""
    email = email.strip().lower()
    for student in students:
        if student["id"] != ignore_id and student["email"].lower() == email:
            raise ValueError(
                f"The e-mail '{email}' is already used by {student['id']} ({student['name']})."
            )


# ---------------------------------------------------------------------------
# Create / Read / Update / Delete
# ---------------------------------------------------------------------------
def add_student(students, name, age, email, department, semester, marks):
    """Validate the data, give it a new ID, append it to the list and return it."""
    raw = {
        "name": name,
        "age": age,
        "email": email,
        "department": department,
        "semester": semester,
        "marks": marks,
    }
    clean = {field: FIELD_VALIDATORS[field](value) for field, value in raw.items()}
    ensure_email_unique(students, clean["email"])

    record = {"id": generate_student_id(students)}
    record.update(clean)
    students.append(record)
    return record


def find_student(students, student_id):
    """Return the student with this ID or raise StudentNotFoundError."""
    wanted = validators.validate_student_id(student_id)
    for student in students:
        if student["id"] == wanted:
            return student
    raise StudentNotFoundError(f"No student found with ID {wanted}.")


def search_by_name(students, text):
    """Case-insensitive 'contains' search, e.g. 'pri' finds 'Priya Patel'."""
    text = validators.validate_search_text(text).lower()
    return [s for s in students if text in s["name"].lower()]


def update_student(students, student_id, **changes):
    """
    Update the given fields of one student and return the updated record.

    Everything is validated BEFORE anything is changed, so a bad value can
    never leave a record half-updated.
    """
    student = find_student(students, student_id)

    unknown = set(changes) - set(FIELD_VALIDATORS)
    if unknown:
        raise ValueError("Cannot update field(s): " + ", ".join(sorted(unknown)) + ".")

    clean = {field: FIELD_VALIDATORS[field](value) for field, value in changes.items()}
    if "email" in clean:
        ensure_email_unique(students, clean["email"], ignore_id=student["id"])

    student.update(clean)
    return student


def delete_student(students, student_id):
    """Remove the student from the list and return the removed record."""
    student = find_student(students, student_id)
    students.remove(student)
    return student


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------
def sort_students(students, sort_by="id", descending=False):
    """Return a NEW sorted list ('id', 'name' or 'marks'); the original is unchanged."""
    sort_keys = {
        "id": lambda s: id_number(s["id"]),
        "name": lambda s: s["name"].lower(),
        "marks": lambda s: s["marks"],
    }
    if sort_by not in sort_keys:
        raise ValueError("Sort field must be one of: id, name, marks.")
    return sorted(students, key=sort_keys[sort_by], reverse=descending)

"""
data_storage.py - Persistent storage of student records.

This module answers one question: "How do student records get saved to and
loaded from disk?"  It uses file_handler for the raw JSON work and
validators to make sure the loaded data is trustworthy.
"""

from pathlib import Path

import file_handler
import validators
from config import SAMPLE_FILE, STUDENTS_FILE
from file_handler import CorruptDataError, DataFileError


def _validate_all(raw_data):
    """Check the structure of loaded JSON and return a clean list of students."""
    if not isinstance(raw_data, list):
        raise CorruptDataError("the file must contain a list of student records.")

    cleaned = []
    seen_ids = set()
    seen_emails = set()
    for position, record in enumerate(raw_data, start=1):
        try:
            student = validators.validate_student_record(record)
        except ValueError as error:
            raise CorruptDataError(f"record #{position} is invalid: {error}") from error
        if student["id"] in seen_ids:
            raise CorruptDataError(f"duplicate student ID {student['id']}.")
        if student["email"] in seen_emails:
            raise CorruptDataError(f"duplicate e-mail {student['email']}.")
        seen_ids.add(student["id"])
        seen_emails.add(student["email"])
        cleaned.append(student)
    return cleaned


def load_students(path=STUDENTS_FILE):
    """
    Load all students from the JSON file.

    * Missing or empty file  -> returns an empty list.
    * Damaged file           -> the file is renamed to '*.corrupt-<time>' (so no
      data is lost) and DataFileError is raised; the caller can then start fresh.
    """
    try:
        raw_data = file_handler.read_json(path, default=[])
        return _validate_all(raw_data)
    except CorruptDataError as error:
        backup = file_handler.backup_corrupt_file(path)
        raise DataFileError(
            f"Data file problem: {error} The damaged file was kept as "
            f"'{backup.name}' and the program will start with an empty list."
        ) from error


def save_students(students, path=STUDENTS_FILE):
    """Write the complete list of students to the JSON file."""
    file_handler.write_json(path, students)


def load_sample_data(path=SAMPLE_FILE):
    """Return the built-in demo students (the sample file itself is never changed)."""
    if not Path(path).exists():
        raise DataFileError(f"Sample data file not found: {path}")
    return load_students(path)

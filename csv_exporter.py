"""
csv_exporter.py - Export reports to CSV files (they open directly in Excel).

Two exports are available:
    * export_students_csv  - one row per student (with percentage and grade)
    * export_summary_csv   - class statistics as "Metric, Value" rows
"""

import csv
from datetime import datetime
from pathlib import Path

import file_handler
from config import EXPORT_DIR
from file_handler import DataFileError
from report_generator import calculate_statistics
from student_operations import with_performance

STUDENT_COLUMNS = [
    "ID", "Name", "Age", "Email", "Department", "Semester",
    "Marks", "Percentage", "Grade", "Result",
]


def _build_path(export_dir, filename, prefix):
    """Create the output path; a timestamped name is used if none is given."""
    if filename:
        name = Path(filename).name          # drop any folders for safety
        if not name.lower().endswith(".csv"):
            name += ".csv"
    else:
        name = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Path(export_dir) / name


def _write_rows(path, header, rows):
    """Write a header and rows to a CSV file."""
    try:
        file_handler.ensure_directory(path.parent)
        # utf-8-sig adds a small marker so Excel reads the file correctly.
        with open(path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows)
    except OSError as error:
        raise DataFileError(
            f"Could not write '{path}': {error}. If the file is open in Excel, close it and try again."
        ) from error


def export_students_csv(students, export_dir=EXPORT_DIR, filename=None):
    """Export every student to a CSV file and return the file path."""
    if not students:
        raise ValueError("There are no student records to export.")
    path = _build_path(export_dir, filename, "student_report")
    rows = []
    for student in students:
        s = with_performance(student)
        rows.append([
            s["id"], s["name"], s["age"], s["email"], s["department"], s["semester"],
            s["marks"], s["percentage"], s["grade"], s["result"],
        ])
    _write_rows(path, STUDENT_COLUMNS, rows)
    return path


def export_summary_csv(students, export_dir=EXPORT_DIR, filename=None):
    """Export the class statistics to a CSV file and return the file path."""
    stats = calculate_statistics(students)
    if stats is None:
        raise ValueError("There are no student records to summarise.")
    path = _build_path(export_dir, filename, "class_summary")

    rows = [
        ["Total students", stats["total_students"]],
        ["Average marks", stats["average_marks"]],
        ["Average percentage", stats["average_percentage"]],
        ["Median marks", stats["median_marks"]],
        ["Standard deviation", stats["std_deviation"]],
        ["Highest marks", stats["highest_marks"]],
        ["Class topper(s)", "; ".join(stats["highest_scorers"])],
        ["Lowest marks", stats["lowest_marks"]],
        ["Passed", stats["pass_count"]],
        ["Failed", stats["fail_count"]],
        ["Pass percentage", stats["pass_percentage"]],
    ]
    for grade, count in stats["grade_distribution"].items():
        rows.append([f"Grade {grade}", count])
    for department, info in stats["department_summary"].items():
        rows.append([
            f"Department {department}",
            f"{info['count']} student(s), average {info['average_percentage']}%",
        ])
    _write_rows(path, ["Metric", "Value"], rows)
    return path

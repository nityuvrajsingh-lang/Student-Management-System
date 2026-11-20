"""
main.py - Entry point of the Student Management System (console application).

Run it with:
    python main.py

This file only handles the user interface (menus, prompts, printing).
All real work is delegated to the other modules:
    student_operations  -> add / search / update / delete / sort / grades
    report_generator    -> topper, statistics, formatted reports
    csv_exporter        -> CSV export
    data_storage        -> loading and saving the JSON database
"""

import config
import csv_exporter
import data_storage
import report_generator as reports
import student_operations as ops
import validators
from file_handler import DataFileError

WIDTH = 60

MENU = f"""
{'=' * WIDTH}
{'STUDENT MANAGEMENT SYSTEM'.center(WIDTH)}
{'=' * WIDTH}
   1. Add Student
   2. View All Students
   3. Search Student (by ID or Name)
   4. Update Student
   5. Delete Student
   6. Sort Students
   7. Show Class Topper
   8. Class Statistics Report
   9. Export Reports to CSV
  10. Load Sample Data
   0. Exit
{'-' * WIDTH}"""


# ---------------------------------------------------------------------------
# Small input / output helpers
# ---------------------------------------------------------------------------
class CancelInput(Exception):
    """Raised when the user types 'cancel' at a prompt."""


def print_header(title):
    print("\n" + "=" * WIDTH)
    print(title.center(WIDTH))
    print("=" * WIDTH)


def pause():
    input("\nPress Enter to continue...")


def ask(prompt, validator=None, current=None):
    """
    Ask until the answer is valid.

    * validator: function that returns a cleaned value or raises ValueError
    * current:   if given, pressing Enter keeps this value (used when updating)
    * typing 'cancel' returns to the main menu
    """
    while True:
        raw = input(prompt).strip()
        if raw.lower() == "cancel":
            raise CancelInput()
        if raw == "" and current is not None:
            return current
        try:
            return validator(raw) if validator else raw
        except ValueError as error:
            print(f"  ! {error}")


def confirm(prompt):
    """Ask a yes/no question and return True for yes."""
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  ! Please type y or n.")


def choice_validator(options):
    """Build a validator that accepts only one of the given option strings."""
    def check(value):
        if value not in options:
            raise ValueError("Please choose one of: " + ", ".join(options))
        return value
    return check


def unique_email_validator(students, ignore_id=None):
    """Validator that checks the format AND that nobody else uses the e-mail."""
    def check(value):
        email = validators.validate_email(value)
        ops.ensure_email_unique(students, email, ignore_id)
        return email
    return check


def field(label):
    """Format a prompt label so all prompts line up."""
    return f"{label:<26}: "


def save(students):
    data_storage.save_students(students)
    print("  (changes saved to disk)")


# ---------------------------------------------------------------------------
# Menu actions - each receives the in-memory list of students
# ---------------------------------------------------------------------------
def add_student_flow(students):
    print_header("ADD NEW STUDENT")
    print("(type 'cancel' at any prompt to return to the menu)")
    print(f"New student ID will be: {ops.generate_student_id(students)}\n")

    name = ask(field("Full name"), validators.validate_name)
    age = ask(field(f"Age ({config.MIN_AGE}-{config.MAX_AGE})"), validators.validate_age)
    email = ask(field("E-mail"), unique_email_validator(students))
    print("  Departments: " + ", ".join(config.DEPARTMENTS))
    department = ask(field("Department"), validators.validate_department)
    semester = ask(
        field(f"Semester ({config.MIN_SEMESTER}-{config.MAX_SEMESTER})"),
        validators.validate_semester,
    )
    marks = ask(field(f"Total marks (0-{config.MAX_MARKS})"), validators.validate_marks)

    student = ops.add_student(students, name, age, email, department, semester, marks)
    print(f"\nStudent added successfully with ID {student['id']}.")
    print(reports.format_student_card(student))
    save(students)


def view_all_flow(students):
    print_header("ALL STUDENTS")
    print(reports.format_student_table(students))


def search_student_flow(students):
    print_header("SEARCH STUDENT")
    print("  1. Search by ID")
    print("  2. Search by Name")
    choice = ask("Choose (1-2): ", choice_validator(["1", "2"]))

    if choice == "1":
        student_id = ask(
            "Enter student ID (e.g. STU001 or just 1): ", validators.validate_student_id
        )
        student = ops.find_student(students, student_id)
        print("\n" + reports.format_student_card(student))
    else:
        text = ask("Enter name (or part of a name): ", validators.validate_search_text)
        matches = ops.search_by_name(students, text)
        if not matches:
            print(f"\nNo student found whose name contains '{text}'.")
        else:
            print(f"\n{len(matches)} match(es) found for '{text}':\n")
            print(reports.format_student_table(matches))


def update_student_flow(students):
    print_header("UPDATE STUDENT")
    print("(type 'cancel' at any prompt to return to the menu)")
    student_id = ask("Enter student ID to update: ", validators.validate_student_id)
    student = ops.find_student(students, student_id)

    print("\nCurrent record:")
    print(reports.format_student_card(student))
    print("Press Enter to keep the current value of a field.\n")

    changes = {
        "name": ask(field(f"Name [{student['name']}]"), validators.validate_name, student["name"]),
        "age": ask(field(f"Age [{student['age']}]"), validators.validate_age, student["age"]),
        "email": ask(
            field(f"E-mail [{student['email']}]"),
            unique_email_validator(students, student["id"]),
            student["email"],
        ),
        "department": ask(
            field(f"Department [{student['department']}]"),
            validators.validate_department,
            student["department"],
        ),
        "semester": ask(
            field(f"Semester [{student['semester']}]"),
            validators.validate_semester,
            student["semester"],
        ),
        "marks": ask(
            field(f"Marks [{student['marks']}]"), validators.validate_marks, student["marks"]
        ),
    }
    updated = ops.update_student(students, student["id"], **changes)
    print("\nStudent updated successfully:")
    print(reports.format_student_card(updated))
    save(students)


def delete_student_flow(students):
    print_header("DELETE STUDENT")
    student_id = ask("Enter student ID to delete: ", validators.validate_student_id)
    student = ops.find_student(students, student_id)
    print("\n" + reports.format_student_card(student))

    if not confirm("Delete this student permanently? (y/n): "):
        print("Delete cancelled. No changes made.")
        return
    removed = ops.delete_student(students, student["id"])
    print(f"\nStudent {removed['id']} ({removed['name']}) has been deleted.")
    save(students)


def sort_students_flow(students):
    print_header("SORT STUDENTS")
    if not students:
        print("No students to sort.")
        return
    field_choice = ask("Sort by  1) ID   2) Name   3) Marks : ", choice_validator(["1", "2", "3"]))
    order_choice = ask("Order    1) Ascending   2) Descending : ", choice_validator(["1", "2"]))

    sort_key = {"1": "id", "2": "name", "3": "marks"}[field_choice]
    ordered = ops.sort_students(students, sort_key, descending=(order_choice == "2"))
    direction = "descending" if order_choice == "2" else "ascending"
    print(f"\nStudents sorted by {sort_key} ({direction}):\n")
    print(reports.format_student_table(ordered))


def topper_flow(students):
    print_header("CLASS TOPPER")
    print(reports.format_topper_report(reports.get_toppers(students)))


def statistics_flow(students):
    print()
    print(reports.format_statistics_report(reports.calculate_statistics(students)))


def export_csv_flow(students):
    print_header("EXPORT REPORTS TO CSV")
    student_file = csv_exporter.export_students_csv(students)
    summary_file = csv_exporter.export_summary_csv(students)
    print("Reports exported successfully:")
    print(f"  Student report : {student_file}")
    print(f"  Class summary  : {summary_file}")


def load_sample_flow(students):
    print_header("LOAD SAMPLE DATA")
    if not confirm("This REPLACES all current records with sample data. Continue? (y/n): "):
        print("Cancelled. No changes made.")
        return
    sample = data_storage.load_sample_data()
    students[:] = sample        # change the list in place so the main loop sees it
    print(f"Loaded {len(students)} sample students.")
    save(students)


# ---------------------------------------------------------------------------
# Main program loop
# ---------------------------------------------------------------------------
ACTIONS = {
    "1": add_student_flow,
    "2": view_all_flow,
    "3": search_student_flow,
    "4": update_student_flow,
    "5": delete_student_flow,
    "6": sort_students_flow,
    "7": topper_flow,
    "8": statistics_flow,
    "9": export_csv_flow,
    "10": load_sample_flow,
}


def load_database():
    """Load students at start-up; on a damaged file, warn and start empty."""
    try:
        students = data_storage.load_students()
        print(f"Loaded {len(students)} student record(s) from {config.STUDENTS_FILE.name}.")
        return students
    except DataFileError as error:
        print(f"\nWARNING: {error}\n")
        return []


def main():
    students = load_database()
    try:
        while True:
            print(MENU)
            choice = input("Enter your choice (0-10): ").strip()
            if choice == "0":
                print("\nThank you for using the Student Management System. Goodbye!")
                break
            action = ACTIONS.get(choice)
            if action is None:
                print("\n  ! Invalid choice. Please enter a number from 0 to 10.")
                continue
            try:
                action(students)
            except CancelInput:
                print("\nCancelled. Returning to the main menu.")
            except (ValueError, ops.StudentNotFoundError) as error:
                print(f"\nError: {error}")
            except DataFileError as error:
                print(f"\nFile error: {error}")
            pause()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram interrupted. Saved data is safe. Goodbye!")


if __name__ == "__main__":
    main()

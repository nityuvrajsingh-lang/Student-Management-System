# Student Management System (GUI + Console)

## Run the graphical application (recommended)

```bash
python gui.py
```

On Windows, if needed: `py gui.py`. The graphical interface uses Python Tkinter and normally requires no additional installation.

## Run the original console application

```bash
python main.py
```

# Student Management System

A complete, menu-driven **console application in Python** for managing student records.
It stores data permanently in a **JSON file**, calculates percentage and grade automatically,
produces class statistics, and exports reports to **CSV**. It uses only the Python standard
library, so there is nothing to install.

---

## Features

| Area | What it does |
|------|--------------|
| **Add** | Creates a student with an automatic unique ID (`STU001`, `STU002`, ...) |
| **Search** | By ID (`STU001`, `stu1` or just `1`) or by name (partial, case-insensitive) |
| **Update** | Edit any field; press Enter to keep the current value |
| **Delete** | Removes a record after a yes/no confirmation |
| **Persistence** | Every change is saved immediately to `data/students.json` |
| **Calculations** | Percentage, grade (A+ to F) and PASS/FAIL result, calculated automatically |
| **Sorting** | By ID, name or marks - ascending or descending |
| **Topper** | Finds the class topper (handles ties) |
| **Statistics** | Average, median, standard deviation, highest/lowest, pass rate, grade distribution, department summary, top 3 |
| **CSV export** | Full student report + class summary, ready to open in Excel |
| **Validation** | Every input is checked; invalid input is re-asked instead of crashing |
| **Safety** | Damaged data files are backed up automatically; saves are crash-safe |
| **Sample data** | 12 ready-made students; reload them any time from the menu |

Student fields: **ID, name, age, e-mail, department, semester, marks**.
Percentage, grade and result are *derived* from marks, so they are calculated when needed and never stored.

---

## Project structure

```
student_management_system/
├── main.py                  # Main application: menus and user interaction
├── student_operations.py    # Student operations: add, search, update, delete, sort, grades
├── file_handler.py          # File handling: safe JSON read/write, backup of damaged files
├── data_storage.py          # Data storage: load/save the student database
├── report_generator.py      # Report generation: topper, statistics, formatted text
├── csv_exporter.py          # CSV exports: student report and class summary
├── validators.py            # Input validation rules
├── config.py                # Settings: file paths, grading scale, limits
├── requirements.txt         # (no third-party packages needed)
├── README.md
├── .gitignore
├── data/
│   ├── students.json        # live database (created/updated by the program)
│   └── sample_students.json # demo data (never modified)
├── exports/                 # generated CSV reports appear here
├── tests/
│   └── test_student_system.py   # 48 automated tests
└── docs/
    ├── PROJECT_REPORT.md / .docx
    ├── DEMO_AND_SCREENSHOTS.md
    └── VIVA_QA.md
```

### How the modules fit together

```
                  main.py  (menus, prompts, printing)
                     |
     +---------------+------------------+------------------+
     |               |                  |                  |
student_operations  report_generator  csv_exporter     data_storage
 (CRUD, grades)     (stats, text)     (CSV files)      (load / save)
     |                   |                  |                  |
     +----- validators --+                  +---- file_handler +
                  \                                 /
                   +----------- config.py ---------+
```

Rule of thumb: **only `main.py` prints or asks for input.** All other modules just take data and
return data, which is why they are easy to test.

---

## Requirements

* Python **3.8 or newer** (check with `python --version`)
* VS Code with the *Python* extension (recommended, not required)
* No `pip install` is needed

---

## Setup in VS Code

**Option A - use the provided folder (fastest)**

1. Extract `student_management_system.zip`.
2. In VS Code: **File > Open Folder...** and choose the `student_management_system` folder.
3. Open the terminal: **Terminal > New Terminal** (shortcut: `` Ctrl+` ``).

**Option B - create the structure yourself**

Run these in a terminal, then create each file inside the folder shown in the structure above
and paste the code into it.

Windows (PowerShell):
```powershell
mkdir student_management_system
cd student_management_system
mkdir data, exports, tests, docs
code .
```

macOS / Linux:
```bash
mkdir -p student_management_system/{data,exports,tests,docs}
cd student_management_system
code .
```

Then copy `data/sample_students.json` to `data/students.json` to start with demo data.

---

## Run the application

```bash
python main.py
```

On macOS/Linux use `python3 main.py`. On Windows, `py main.py` also works.
Make sure the terminal is inside the project folder (the one containing `main.py`).

### Run the automated tests

```bash
python -m unittest discover -s tests -v
```

Expected result: `Ran 48 tests ... OK`. The tests use temporary folders, so they never touch your real data.

---

## Using the program

```
============================================================
                 STUDENT MANAGEMENT SYSTEM
============================================================
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
```

Tips:

* Type **`cancel`** at any prompt while adding/updating/searching to return to the menu.
* When updating, press **Enter** to keep a field unchanged.
* Sorting only changes what is *displayed*; stored order stays by ID.
* CSV files are saved in the `exports/` folder with a timestamp in the name.
* To reset the demo data at any time, choose option **10**.

### Validation rules

| Field | Rule |
|-------|------|
| Name | 2-50 characters, English letters, spaces, `.`, `'`, `-`; stored in Title Case |
| Age | Whole number, 16-60 |
| E-mail | Valid format, **unique** across students, stored in lower case |
| Department | One of `CSE, IT, AIML, ECE, EEE, ME, CE` |
| Semester | Whole number, 1-8 |
| Marks | Number from 0 to 500 (total of five 100-mark subjects) |

### Grading scale (percentage = marks / 500 x 100)

| Percentage | Grade | | Percentage | Grade |
|-----------:|:-----:|-|-----------:|:-----:|
| 90 and above | A+ | | 50 - 59.99 | C |
| 80 - 89.99 | A | | 40 - 49.99 | D |
| 70 - 79.99 | B+ | | below 40 | F (FAIL) |
| 60 - 69.99 | B | | | |

Change the scale, maximum marks, departments or limits in `config.py` - no other file needs editing.

### Data format (`data/students.json`)

```json
{
    "id": "STU001",
    "name": "Aarav Sharma",
    "age": 20,
    "email": "aarav.sharma@example.com",
    "department": "CSE",
    "semester": 5,
    "marks": 432
}
```

---

## Error handling at a glance

| Situation | What happens |
|-----------|--------------|
| Invalid input | Friendly message, the question is asked again |
| Duplicate e-mail | Rejected with the name of the student who already uses it |
| Unknown student ID | "No student found" message, back to menu |
| Data file missing/empty | Program starts with an empty list |
| Data file damaged | Renamed to `students.json.corrupt-<time>`, program starts empty, nothing is lost |
| Save/export fails (e.g. CSV open in Excel) | Clear message, program keeps running |
| Ctrl+C or closed input | Clean exit (saved data is already safe) |

---

## Known limitations

* If the **most recent** student is deleted, the next new student reuses that ID (IDs are `highest + 1`).
* Single-user program: it does not lock the file against two copies running at once.
* Marks are one total out of 500, not subject-wise.
* Names accept English letters only.

## Possible enhancements

Subject-wise marks, login/roles, SQLite instead of JSON, a Tkinter or Flask front end, department filters, charts with matplotlib, PDF reports.

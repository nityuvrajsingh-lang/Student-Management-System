"""
report_generator.py - Statistics and text reports.

Functions named get_* / calculate_* return data (lists, dictionaries).
Functions named format_* turn that data into text ready to print.
"""

import statistics

from config import GRADE_SCALE, MAX_MARKS
from student_operations import calculate_percentage, with_performance

REPORT_WIDTH = 60


# ---------------------------------------------------------------------------
# Data functions
# ---------------------------------------------------------------------------
def get_toppers(students):
    """Return every student who has the highest marks (handles ties)."""
    if not students:
        return []
    best = max(s["marks"] for s in students)
    return [s for s in students if s["marks"] == best]


def get_top_performers(students, count=3):
    """Return the `count` students with the highest marks, best first."""
    return sorted(students, key=lambda s: s["marks"], reverse=True)[:count]


def calculate_statistics(students):
    """
    Build a dictionary of class statistics, or return None for an empty class.
    """
    if not students:
        return None

    marks = [s["marks"] for s in students]
    enriched = [with_performance(s) for s in students]
    total = len(students)

    highest, lowest = max(marks), min(marks)
    passed = sum(1 for s in enriched if s["result"] == "PASS")

    grade_distribution = {grade: 0 for _, grade in GRADE_SCALE}
    for student in enriched:
        grade_distribution[student["grade"]] += 1

    groups = {}
    for student in enriched:
        groups.setdefault(student["department"], []).append(student)
    department_summary = {}
    for department in sorted(groups):
        members = groups[department]
        department_summary[department] = {
            "count": len(members),
            "average_percentage": round(
                sum(m["percentage"] for m in members) / len(members), 2
            ),
        }

    average_marks = statistics.mean(marks)
    return {
        "total_students": total,
        "average_marks": round(average_marks, 2),
        "average_percentage": round(average_marks / MAX_MARKS * 100, 2),
        "median_marks": round(statistics.median(marks), 2),
        "std_deviation": round(statistics.pstdev(marks), 2),
        "highest_marks": highest,
        "highest_scorers": [s["name"] for s in students if s["marks"] == highest],
        "lowest_marks": lowest,
        "lowest_scorers": [s["name"] for s in students if s["marks"] == lowest],
        "pass_count": passed,
        "fail_count": total - passed,
        "pass_percentage": round(passed / total * 100, 2),
        "grade_distribution": grade_distribution,
        "department_summary": department_summary,
        "top_performers": [
            {
                "id": s["id"],
                "name": s["name"],
                "marks": s["marks"],
                "percentage": calculate_percentage(s["marks"]),
            }
            for s in get_top_performers(students, 3)
        ],
    }


# ---------------------------------------------------------------------------
# Text formatting
# ---------------------------------------------------------------------------
def _clip(text, width):
    """Shorten text with '...' so table columns stay aligned."""
    text = str(text)
    return text if len(text) <= width else text[: width - 3] + "..."


def format_student_table(students):
    """Return a neat text table of students (with percentage and grade)."""
    if not students:
        return "No students to display."

    header = (
        f"{'ID':<7} {'Name':<22} {'Age':>3} {'Email':<30} {'Dept':<6} "
        f"{'Sem':>3} {'Marks':>7} {'%':>7} {'Grade':<5}"
    )
    lines = [header, "-" * len(header)]
    for student in students:
        s = with_performance(student)
        lines.append(
            f"{s['id']:<7} {_clip(s['name'], 22):<22} {s['age']:>3} "
            f"{_clip(s['email'], 30):<30} {s['department']:<6} {s['semester']:>3} "
            f"{s['marks']:>7.2f} {s['percentage']:>7.2f} {s['grade']:<5}"
        )
    lines.append("-" * len(header))
    lines.append(f"Marks are out of {MAX_MARKS}.  Total records shown: {len(students)}")
    return "\n".join(lines)


def format_student_card(student):
    """Return a detailed multi-line view of one student."""
    s = with_performance(student)
    return "\n".join(
        [
            "-" * 40,
            f"  ID          : {s['id']}",
            f"  Name        : {s['name']}",
            f"  Age         : {s['age']}",
            f"  Email       : {s['email']}",
            f"  Department  : {s['department']}",
            f"  Semester    : {s['semester']}",
            f"  Marks       : {s['marks']:.2f} / {MAX_MARKS}",
            f"  Percentage  : {s['percentage']:.2f}%",
            f"  Grade       : {s['grade']}",
            f"  Result      : {s['result']}",
            "-" * 40,
        ]
    )


def format_topper_report(toppers):
    """Return text describing the class topper(s)."""
    if not toppers:
        return "No student data available to find a topper."
    lines = []
    if len(toppers) > 1:
        lines.append(f"There is a tie: {len(toppers)} students share the top score.\n")
    else:
        lines.append("Class topper:\n")
    for student in toppers:
        lines.append(format_student_card(student))
    return "\n".join(lines)


def format_statistics_report(stats):
    """Return the full class performance report as text."""
    if stats is None:
        return "No student data available to generate a report."

    bar = "=" * REPORT_WIDTH
    thin = "-" * REPORT_WIDTH
    highest = ", ".join(stats["highest_scorers"])
    lowest = ", ".join(stats["lowest_scorers"])
    lines = [
        bar,
        "CLASS PERFORMANCE REPORT".center(REPORT_WIDTH),
        bar,
        f"Total students      : {stats['total_students']}",
        f"Average marks       : {stats['average_marks']:.2f} / {MAX_MARKS}",
        f"Average percentage  : {stats['average_percentage']:.2f}%",
        f"Median marks        : {stats['median_marks']:.2f}",
        f"Standard deviation  : {stats['std_deviation']:.2f}",
        f"Highest marks       : {stats['highest_marks']:.2f}  ({highest})",
        f"Lowest marks        : {stats['lowest_marks']:.2f}  ({lowest})",
        f"Passed              : {stats['pass_count']}",
        f"Failed              : {stats['fail_count']}",
        f"Pass percentage     : {stats['pass_percentage']:.2f}%",
        "",
        "Top performers",
        thin,
    ]
    for rank, item in enumerate(stats["top_performers"], start=1):
        lines.append(
            f"  {rank}. {item['name']:<22} {item['id']}  "
            f"{item['marks']:.2f} marks  ({item['percentage']:.2f}%)"
        )

    lines += ["", "Grade distribution", thin]
    biggest = max(stats["grade_distribution"].values())
    for grade, count in stats["grade_distribution"].items():
        bars = "#" * max(1, round(count / biggest * 30)) if count else ""
        lines.append(f"  {grade:<3} {count:>4}  {bars}")

    lines += ["", "Department summary", thin, f"  {'Dept':<8}{'Students':>9}{'Avg %':>10}"]
    for department, info in stats["department_summary"].items():
        lines.append(
            f"  {department:<8}{info['count']:>9}{info['average_percentage']:>10.2f}"
        )
    lines.append(bar)
    return "\n".join(lines)

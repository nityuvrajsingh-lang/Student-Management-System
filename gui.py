"""Tkinter GUI for the Student Management System."""
import tkinter as tk
from tkinter import ttk, messagebox

import data_storage
import csv_exporter
import report_generator
from student_operations import add_student, update_student, delete_student, with_performance, sort_students
from file_handler import DataFileError
from config import EXPORT_DIR, MAX_MARKS

BG = "#f4f7fb"
NAVY = "#172554"
TEAL = "#0f9d91"
WHITE = "#ffffff"
TEXT = "#1e293b"
MUTED = "#64748b"


class StudentManagementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Management System")
        self.geometry("1180x760")
        self.minsize(1000, 650)
        self.configure(bg=BG)
        try:
            self.students = data_storage.load_students()
        except DataFileError as exc:
            messagebox.showwarning("Data file warning", str(exc))
            self.students = []
        self.selected_id = None
        self._style()
        self._build()
        self.refresh()

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background=WHITE, foreground=TEXT, rowheight=30, fieldbackground=WHITE, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#e2e8f0", foreground=NAVY, font=("Segoe UI", 9, "bold"), padding=8)
        style.map("Treeview", background=[("selected", "#ccfbf1")], foreground=[("selected", NAVY)])
        style.configure("TCombobox", padding=6)

    def _build(self):
        header = tk.Frame(self, bg=NAVY, height=88)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="STUDENT MANAGEMENT SYSTEM", bg=NAVY, fg=WHITE,
                 font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=26, pady=(16, 0))
        tk.Label(header, text="Student records • Academic performance • Reports", bg=NAVY,
                 fg="#cbd5e1", font=("Segoe UI", 10)).pack(anchor="w", padx=28)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=22, pady=18)

        stats = tk.Frame(body, bg=BG)
        stats.pack(fill="x", pady=(0, 14))
        self.stat_labels = {}
        for key, title in [("total", "TOTAL STUDENTS"), ("average", "CLASS AVERAGE"), ("passed", "PASSED"), ("topper", "TOP MARKS")]:
            card = tk.Frame(stats, bg=WHITE, highlightbackground="#e2e8f0", highlightthickness=1)
            card.pack(side="left", fill="x", expand=True, padx=(0, 10))
            tk.Label(card, text=title, bg=WHITE, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=14, pady=(10, 2))
            value = tk.Label(card, text="—", bg=WHITE, fg=NAVY, font=("Segoe UI", 19, "bold"))
            value.pack(anchor="w", padx=14, pady=(0, 10))
            self.stat_labels[key] = value

        content = tk.Frame(body, bg=BG)
        content.pack(fill="both", expand=True)
        left = tk.Frame(content, bg=WHITE, width=330, highlightbackground="#e2e8f0", highlightthickness=1)
        left.pack(side="left", fill="y", padx=(0, 14))
        left.pack_propagate(False)
        tk.Label(left, text="STUDENT DETAILS", bg=WHITE, fg=NAVY, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=18, pady=(16, 12))
        self.vars = {k: tk.StringVar() for k in ["name", "age", "email", "department", "semester", "marks"]}
        fields = [("Full name", "name"), ("Age", "age"), ("Email", "email"), ("Department", "department"), ("Semester", "semester"), (f"Total marks (out of {MAX_MARKS})", "marks")]
        for label, key in fields:
            tk.Label(left, text=label, bg=WHITE, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=18, pady=(5, 2))
            if key == "department":
                widget = ttk.Combobox(left, textvariable=self.vars[key], values=["CSE", "IT", "AIML", "ECE", "EEE", "ME", "CE"], state="readonly")
            else:
                widget = tk.Entry(left, textvariable=self.vars[key], font=("Segoe UI", 10), relief="solid", bd=1)
            widget.pack(fill="x", padx=18, ipady=5)
        buttons = tk.Frame(left, bg=WHITE)
        buttons.pack(fill="x", padx=18, pady=14)
        self._button(buttons, "Add Student", TEAL, self.add).pack(fill="x", pady=3)
        self._button(buttons, "Update Selected", NAVY, self.update).pack(fill="x", pady=3)
        self._button(buttons, "Delete Selected", "#b91c1c", self.delete).pack(fill="x", pady=3)
        self._button(buttons, "Clear Form", "#475569", self.clear_form).pack(fill="x", pady=3)

        right = tk.Frame(content, bg=WHITE, highlightbackground="#e2e8f0", highlightthickness=1)
        right.pack(side="left", fill="both", expand=True)
        top = tk.Frame(right, bg=WHITE)
        top.pack(fill="x", padx=16, pady=14)
        tk.Label(top, text="STUDENT DIRECTORY", bg=WHITE, fg=NAVY, font=("Segoe UI", 12, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        search = tk.Entry(top, textvariable=self.search_var, width=25, font=("Segoe UI", 10), relief="solid", bd=1)
        search.pack(side="right", ipady=5)
        search.insert(0, "")
        self.search_var.trace_add("write", lambda *_: self.refresh())
        tk.Label(top, text="Search", bg=WHITE, fg=MUTED, font=("Segoe UI", 9)).pack(side="right", padx=8)

        columns = ("id", "name", "department", "semester", "marks", "percentage", "grade", "result")
        self.tree = ttk.Treeview(right, columns=columns, show="headings", selectmode="browse")
        headings = {"id":"Student ID", "name":"Name", "department":"Dept.", "semester":"Sem.", "marks":"Marks", "percentage":"Percent", "grade":"Grade", "result":"Result"}
        widths = {"id":85,"name":155,"department":65,"semester":55,"marks":75,"percentage":80,"grade":60,"result":65}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center" if col not in ("name",) else "w")
        self.tree.pack(fill="both", expand=True, padx=14, pady=(0, 10))
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        actions = tk.Frame(right, bg=WHITE)
        actions.pack(fill="x", padx=14, pady=(0, 14))
        self._button(actions, "Class Report", "#334155", self.show_report).pack(side="left", padx=(0, 7))
        self._button(actions, "Export CSV", TEAL, self.export_csv).pack(side="left", padx=7)
        self._button(actions, "Load Demo Data", "#475569", self.load_demo).pack(side="left", padx=7)
        self._button(actions, "Refresh", "#475569", self.refresh).pack(side="right")

        footer = tk.Label(self, text="Data is saved automatically in data/students.json", bg=BG, fg=MUTED, font=("Segoe UI", 9))
        footer.pack(anchor="w", padx=26, pady=(0, 10))

    def _button(self, parent, text, color, command):
        return tk.Button(parent, text=text, command=command, bg=color, fg=WHITE, activebackground=color,
                         activeforeground=WHITE, relief="flat", cursor="hand2", font=("Segoe UI", 9, "bold"), padx=12, pady=8)

    def persist(self):
        data_storage.save_students(self.students)

    def form_values(self):
        return {k: v.get().strip() for k, v in self.vars.items()}

    def add(self):
        try:
            v = self.form_values()
            add_student(self.students, v["name"], v["age"], v["email"], v["department"], v["semester"], v["marks"])
            self.persist(); self.refresh(); self.clear_form()
            messagebox.showinfo("Success", "Student record added successfully.")
        except (ValueError, DataFileError) as exc:
            messagebox.showerror("Unable to add student", str(exc))

    def update(self):
        if not self.selected_id:
            messagebox.showwarning("Select a student", "Select a student from the table first."); return
        try:
            v = self.form_values()
            update_student(self.students, self.selected_id, **v)
            self.persist(); self.refresh(); self.clear_form()
            messagebox.showinfo("Success", "Student record updated successfully.")
        except (ValueError, DataFileError) as exc:
            messagebox.showerror("Unable to update student", str(exc))

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("Select a student", "Select a student from the table first."); return
        student = next((s for s in self.students if s["id"] == self.selected_id), None)
        if student and messagebox.askyesno("Confirm deletion", f"Delete {student['name']} ({student['id']})?"):
            try:
                delete_student(self.students, self.selected_id); self.persist(); self.refresh(); self.clear_form()
            except (ValueError, DataFileError) as exc:
                messagebox.showerror("Unable to delete student", str(exc))

    def clear_form(self):
        self.selected_id = None
        for var in self.vars.values(): var.set("")
        self.tree.selection_remove(self.tree.selection())

    def on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected: return
        values = self.tree.item(selected[0], "values")
        self.selected_id = values[0]
        student = next((s for s in self.students if s["id"] == self.selected_id), None)
        if student:
            for key in self.vars: self.vars[key].set(str(student[key]))

    def refresh(self):
        if not hasattr(self, "tree"): return
        query = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
        for item in self.tree.get_children(): self.tree.delete(item)
        records = self.students
        if query:
            records = [s for s in records if query in s["id"].lower() or query in s["name"].lower() or query in s["email"].lower()]
        for s in sort_students(records, "name"):
            p = with_performance(s)
            self.tree.insert("", "end", values=(p["id"], p["name"], p["department"], p["semester"], f"{p['marks']:g}", f"{p['percentage']:.2f}%", p["grade"], p["result"]))
        stats = report_generator.calculate_statistics(self.students)
        self.stat_labels["total"].config(text=str(len(self.students)))
        if stats:
            self.stat_labels["average"].config(text=f"{stats['average_percentage']:.1f}%")
            self.stat_labels["passed"].config(text=f"{stats['pass_count']} / {stats['total_students']}")
            self.stat_labels["topper"].config(text=f"{stats['highest_marks']:g} / {MAX_MARKS}")
        else:
            for key in ("average", "passed", "topper"): self.stat_labels[key].config(text="—")

    def show_report(self):
        stats = report_generator.calculate_statistics(self.students)
        if not stats:
            messagebox.showinfo("Class report", "No student records available yet."); return
        report = report_generator.format_statistics_report(stats)
        win = tk.Toplevel(self); win.title("Class Performance Report"); win.geometry("650x600"); win.configure(bg=WHITE)
        tk.Label(win, text="CLASS PERFORMANCE REPORT", bg=WHITE, fg=NAVY, font=("Segoe UI", 15, "bold")).pack(pady=14)
        box = tk.Text(win, wrap="none", font=("Consolas", 10), bg="#f8fafc", fg=TEXT, padx=14, pady=12)
        box.pack(fill="both", expand=True, padx=14, pady=(0, 14)); box.insert("1.0", report); box.config(state="disabled")

    def export_csv(self):
        try:
            path = csv_exporter.export_students_csv(self.students, EXPORT_DIR)
            csv_exporter.export_summary_csv(self.students, EXPORT_DIR)
            messagebox.showinfo("Export complete", f"Student and class summary CSV files saved in:\n{path.parent}")
        except (ValueError, DataFileError) as exc:
            messagebox.showerror("Export failed", str(exc))

    def load_demo(self):
        if self.students and not messagebox.askyesno("Load demo data", "Demo records will be added to your existing records. Continue?"):
            return
        try:
            samples = data_storage.load_sample_data()
            existing = {s["email"].lower() for s in self.students}
            added = 0
            for sample in samples:
                if sample["email"].lower() not in existing and not any(x["id"] == sample["id"] for x in self.students):
                    record = dict(sample)
                    record["id"] = f"STU{max([int(x['id'][3:]) for x in self.students if x['id'].startswith('STU') and x['id'][3:].isdigit()] + [0]) + 1:03d}"
                    self.students.append(record); added += 1
            self.persist(); self.refresh()
            messagebox.showinfo("Demo data", f"Added {added} sample student(s).")
        except (DataFileError, OSError) as exc:
            messagebox.showerror("Demo data error", str(exc))


if __name__ == "__main__":
    app = StudentManagementApp()
    app.mainloop()


# ============================================================
# STUDENT LIFE ASSISTANT - PYTHON CCE PROJECT
# ============================================================

import json
import os
from datetime import date

DATA_FILE = "student_data.json"

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
GRAY = "\033[90m"

WIDTH = 60

def new_data():
    return {
        "profile": {"name": "", "class": "", "school": ""},
        "subjects": [],
        "tasks": [],
        "marks": [],
        "timetable": []
    }

data = new_data()


def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except OSError as error:
        print(f"{RED}Save failed: {error}{RESET}")
        return False


def load_data():
    global data
    data = new_data()

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)

            if isinstance(saved, dict):
                if isinstance(saved.get("profile"), dict):
                    data["profile"].update(saved["profile"])

                for key in ("subjects", "tasks", "marks", "timetable"):
                    if isinstance(saved.get(key), list):
                        data[key] = saved[key]

        except (OSError, json.JSONDecodeError):
            print("Saved data could not be read. Starting fresh.")


def clear_screen():
    print("\n" * 3)


def header(title, subtitle=""):
    print(f"\n{CYAN}{BOLD}{'═' * WIDTH}{RESET}")
    print(f"{CYAN}{BOLD}{title.center(WIDTH)}{RESET}")
    if subtitle:
        print(f"{GRAY}{subtitle.center(WIDTH)}{RESET}")
    print(f"{CYAN}{BOLD}{'═' * WIDTH}{RESET}")


def pause():
    input(f"\n{YELLOW}Press ENTER to continue...{RESET}")


def ask_int(prompt, minimum, maximum=None):
    while True:
        try:
            value = int(input(prompt))
            if value < minimum or (maximum is not None and value > maximum):
                print("Number outside the allowed range.")
                continue
            return value
        except ValueError:
            print("Please enter a whole number.")


def ask_float(prompt, minimum, maximum=None):
    while True:
        try:
            value = float(input(prompt))
            if value < minimum or (maximum is not None and value > maximum):
                print("Number outside the allowed range.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")


def profile_manager():
    while True:
        clear_screen()
        header("STUDENT PROFILE")
        p = data["profile"]

        print("Name   :", p.get("name") or "Not set")
        print("Class  :", p.get("class") or "Not set")
        print("School :", p.get("school") or "Not set")
        print("\n1. Edit profile")
        print("0. Back")

        choice = input("\nChoose: ")

        if choice == "1":
            p["name"] = input("Student name: ").strip()
            p["class"] = input("Class: ").strip()
            p["school"] = input("School: ").strip()
            save_data()
            pause()
        elif choice == "0":
            return
        else:
            print("Invalid choice.")


def subjects_manager():
    while True:
        clear_screen()
        header("SUBJECT MANAGER")

        subjects = data["subjects"]
        if subjects:
            for i, subject in enumerate(subjects, 1):
                print(f"  {i:02}. {subject}")
        else:
            print("No subjects added yet.")

        print("\n1. Add subject")
        print("2. Delete subject")
        print("0. Back")

        choice = input("\nChoose: ")

        if choice == "1":
            subject = input("Subject name: ").strip()
            if not subject:
                print("Subject name cannot be empty.")
            elif any(s.lower() == subject.lower() for s in subjects):
                print("That subject already exists.")
            else:
                subjects.append(subject)
                save_data()
                print(f"{GREEN}Subject added!{RESET}")
            pause()

        elif choice == "2":
            if subjects:
                number = ask_int("Subject number: ", 1, len(subjects))
                subjects.pop(number - 1)
                save_data()
                print("Subject deleted.")
            else:
                print("No subjects to delete.")
            pause()

        elif choice == "0":
            return
        else:
            print("Invalid choice.")


def tasks_manager():
    while True:
        clear_screen()
        header("HOMEWORK & TASKS", "PLAN IT • DO IT • COMPLETE IT")

        tasks = data["tasks"]
        if tasks:
            for i, task in enumerate(tasks, 1):
                status = "DONE" if task["completed"] else "PENDING"
                print(f"\n{i}. {task['title']} [{status}]")
                print(f"   Subject: {task['subject']} | Due: {task['due']}")
        else:
            print("No tasks added yet.")

        print("\n1. Add task")
        print("2. Mark completed")
        print("3. Delete task")
        print("0. Back")

        choice = input("\nChoose: ")

        if choice == "1":
            title = input("Task title: ").strip()
            if not title:
                print("Task title is required.")
                pause()
                continue

            subject = input("Subject: ").strip() or "General"
            due = input("Due date: ").strip() or "Not set"

            tasks.append({
                "title": title,
                "subject": subject,
                "due": due,
                "completed": False
            })
            save_data()
            print("Task added.")
            pause()

        elif choice == "2":
            if tasks:
                number = ask_int("Task number: ", 1, len(tasks))
                tasks[number - 1]["completed"] = True
                save_data()
                print("Task completed.")
            else:
                print("No tasks available.")
            pause()

        elif choice == "3":
            if tasks:
                number = ask_int("Task number: ", 1, len(tasks))
                tasks.pop(number - 1)
                save_data()
                print("Task deleted.")
            else:
                print("No tasks available.")
            pause()

        elif choice == "0":
            return
        else:
            print("Invalid choice.")

def get_results():
    total = sum(item["mark"] for item in data["marks"])
    maximum = sum(item["maximum"] for item in data["marks"])
    percentage = total / maximum * 100 if maximum else 0
    return total, maximum, percentage


def get_grade(percentage):
    if percentage >= 90:
        return "A+"
    if percentage >= 80:
        return "A"
    if percentage >= 70:
        return "B+"
    if percentage >= 60:
        return "B"
    if percentage >= 50:
        return "C+"
    if percentage >= 40:
        return "C"
    return "D"


def marks_manager():
    while True:
        clear_screen()
        header("MARKS & RESULTS")

        marks = data["marks"]
        for i, item in enumerate(marks, 1):
            print(f"{i}. {item['subject']}: {item['mark']}/{item['maximum']}")

        if marks:
            total, maximum, percentage = get_results()
            print(f"\nTotal: {total:g}/{maximum:g}")
            print(f"Percentage: {percentage:.2f}%")
            print(f"Grade: {get_grade(percentage)}")
        else:
            print("No marks entered yet.")

        print("\n1. Add marks")
        print("2. Delete marks")
        print("0. Back")
        choice = input("\nChoose: ")

        if choice == "1":
            subject = input("Subject: ").strip()
            if not subject:
                print("Subject is required.")
                pause()
                continue

            maximum = ask_float("Maximum marks: ", 0.01)
            mark = ask_float("Marks obtained: ", 0, maximum)

            marks.append({
                "subject": subject,
                "mark": mark,
                "maximum": maximum
            })
            save_data()
            print("Marks saved.")
            pause()

        elif choice == "2":
            if marks:
                number = ask_int("Entry number: ", 1, len(marks))
                marks.pop(number - 1)
                save_data()
                print("Entry deleted.")
            else:
                print("No marks available.")
            pause()

        elif choice == "0":
            return
        else:
            print("Invalid choice.")


def timetable_manager():
    while True:
        clear_screen()
        header("CLASS TIMETABLE")

        timetable = data["timetable"]
        for i, item in enumerate(timetable, 1):
            print(f"{i}. {item['day']} | {item['time']} | {item['subject']}")

        if not timetable:
            print("No timetable entries yet.")

        print("\n1. Add class")
        print("2. Delete class")
        print("0. Back")
        choice = input("\nChoose: ")

        if choice == "1":
            day = input("Day: ").strip()
            time = input("Time: ").strip()
            subject = input("Subject: ").strip()

            if day and time and subject:
                timetable.append({
                    "day": day,
                    "time": time,
                    "subject": subject
                })
                save_data()
                print("Class added.")
            else:
                print("All fields are required.")
            pause()

        elif choice == "2":
            if timetable:
                number = ask_int("Entry number: ", 1, len(timetable))
                timetable.pop(number - 1)
                save_data()
                print("Class deleted.")
            else:
                print("No entries available.")
            pause()

        elif choice == "0":
            return
        else:
            print("Invalid choice.")


def search_manager():
    clear_screen()
    header("SEARCH STUDY DATA")

    query = input("Enter a keyword: ").strip().lower()
    if not query:
        print("Enter a search keyword.")
        pause()
        return

    found = False

    for subject in data["subjects"]:
        if query in subject.lower():
            print("[SUBJECT]", subject)
            found = True

    for task in data["tasks"]:
        content = f"{task['title']} {task['subject']} {task['due']}"
        if query in content.lower():
            status = "DONE" if task["completed"] else "PENDING"
            print(f"[TASK] {task['title']} - {status} - {task['due']}")
            found = True

    for item in data["marks"]:
        if query in item["subject"].lower():
            print(f"[MARKS] {item['subject']}: {item['mark']}/{item['maximum']}")
            found = True

    for item in data["timetable"]:
        content = f"{item['day']} {item['time']} {item['subject']}"
        if query in content.lower():
            print(f"[CLASS] {item['day']} {item['time']} {item['subject']}")
            found = True

    if not found:
        print("No matching information found.")

    pause()


def dashboard():
    clear_screen()
    header("STUDENT DASHBOARD", "YOUR DAILY STUDY OVERVIEW")

    profile = data["profile"]
    tasks = data["tasks"]
    completed = sum(1 for t in tasks if t["completed"])
    total, maximum, percentage = get_results()

    print(f"\nWelcome, {profile.get('name') or 'Student'}!")
    print(f"Class: {profile.get('class') or 'Not set'}")
    print(f"School: {profile.get('school') or 'Not set'}")

    print("\n" + "-" * WIDTH)
    print(f"Subjects          : {len(data['subjects'])}")
    print(f"Homework tasks    : {len(tasks)}")
    print(f"Completed tasks   : {completed}")
    print(f"Pending tasks     : {len(tasks) - completed}")
    print(f"Timetable entries : {len(data['timetable'])}")
    print(f"Marks percentage  : {percentage:.2f}%")
    print(f"Overall grade     : {get_grade(percentage) if maximum else 'Not available'}")
    print("-" * WIDTH)

    if tasks and completed == len(tasks):
        print(f"{GREEN}Excellent! All your tasks are complete.{RESET}")
    elif tasks:
        print(f"{YELLOW}Keep going. Check your pending tasks!{RESET}")
    else:
        print("Tip: Add a homework task to get started.")

    pause()


def about_project():
    clear_screen()
    header("ABOUT THIS PROJECT")

    print("""
Student Life Assistant
A Python-only student management project.

FEATURES
- Student profile
- Subject management
- Homework and task tracking
- Marks, percentages and grades
- Class timetable
- Search study information
- Dashboard
- JSON data storage

TECHNOLOGY
Python standard library.

This is a terminal application, not a browser website.
""")
    pause()


def main():
    load_data()

    while True:
        clear_screen()
        name = data["profile"].get("name") or "Student"

        print(f"{CYAN}{BOLD}")
        print("╔" + "═" * (WIDTH - 2) + "╗")
        print("║" + "STUDENT LIFE ASSISTANT".center(WIDTH - 2) + "║")
        print("║" + "YOUR PERSONAL STUDY SPACE".center(WIDTH - 2) + "║")
        print("╚" + "═" * (WIDTH - 2) + "╝")
        print(f"{RESET}")
        print(f"Welcome, {name}!  |  {date.today().strftime('%d %B %Y')}")
        print("\n  1. Dashboard          6. Timetable")
        print("  2. Student profile    7. Search")
        print("  3. Subjects           8. Save data")
        print("  4. Homework & tasks   9. About project")
        print("  5. Marks & results    0. Exit")
        print("\n" + "─" * WIDTH)

        choice = input("Choose an option: ").strip()

        if choice == "1":
            dashboard()
        elif choice == "2":
            profile_manager()
        elif choice == "3":
            subjects_manager()
        elif choice == "4":
            tasks_manager()
        elif choice == "5":
            marks_manager()
        elif choice == "6":
            timetable_manager()
        elif choice == "7":
            search_manager()
        elif choice == "8":
            print("Data saved." if save_data() else "Save failed.")
            pause()
        elif choice == "9":
            about_project()
        elif choice == "0":
            save_data()
            print(f"{GREEN}Thank you for using Student Life Assistant!{RESET}")
            break
        else:
            print("Please choose a number from 0 to 9.")
            pause()


if __name__ == "__main__":
    main()

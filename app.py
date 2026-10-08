
import json
from pathlib import Path

import streamlit as st

DATA_FILE = Path("student_data.json")

DEFAULT_DATA = {
    "profile": {"name": "", "class": "", "school": ""},
    "subjects": [],
    "tasks": [],
    "marks": [],
    "timetable": []
}

st.set_page_config(
    page_title="Student Life Assistant",
    page_icon="📚",
    layout="wide"
)


def load_data():
    data = {
        "profile": DEFAULT_DATA["profile"].copy(),
        "subjects": [],
        "tasks": [],
        "marks": [],
        "timetable": []
    }

    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as file:
                saved = json.load(file)

            if isinstance(saved, dict):
                if isinstance(saved.get("profile"), dict):
                    data["profile"].update(saved["profile"])

                for key in ("subjects", "tasks", "marks", "timetable"):
                    if isinstance(saved.get(key), list):
                        data[key] = saved[key]

        except (OSError, json.JSONDecodeError):
            st.warning("Could not read the saved data file.")

    return data


def save_data():
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(st.session_state.data, file, indent=4)
        return True
    except OSError as error:
        st.error(f"Could not save data: {error}")
        return False


if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data


def grade_for(percentage):
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


def results():
    total = sum(float(m.get("mark", 0)) for m in data["marks"])
    maximum = sum(float(m.get("maximum", 0)) for m in data["marks"])
    percentage = total / maximum * 100 if maximum else 0
    return total, maximum, percentage


def refresh_saved_data():
    save_data()
    st.rerun()


# Sidebar navigation
with st.sidebar:
    st.title("📚 Student Life")
    st.caption("Your personal study space")
    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "Student Profile",
            "Subjects",
            "Homework & Tasks",
            "Marks & Results",
            "Timetable",
            "Search",
            "About"
        ]
    )
    st.divider()
    st.caption("Python + Streamlit")


# Page heading
st.title("📚 Student Life Assistant")
st.caption("Organise your studies, track your progress, and stay on top of tasks.")

profile = data["profile"]


# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    name = profile.get("name") or "Student"
    st.subheader(f"Welcome back, {name} 👋")
    st.write(
        f"{profile.get('class') or 'Class not set'} · "
        f"{profile.get('school') or 'School not set'}"
    )

    completed = sum(1 for task in data["tasks"] if task.get("completed", False))
    pending = len(data["tasks"]) - completed
    total, maximum, percentage = results()

    a, b, c, d = st.columns(4)
    a.metric("Subjects", len(data["subjects"]))
    b.metric("Total tasks", len(data["tasks"]))
    c.metric("Pending tasks", pending)
    d.metric("Timetable entries", len(data["timetable"]))

    st.subheader("Academic progress")
    left, right = st.columns(2)
    left.metric("Marks percentage", f"{percentage:.1f}%" if maximum else "Not available")
    right.metric("Overall grade", grade_for(percentage) if maximum else "—")

    if maximum:
        st.progress(min(percentage / 100, 1.0))
        st.caption(f"Marks: {total:g} out of {maximum:g}")

    st.subheader("Homework overview")
    if data["tasks"]:
        for index, task in enumerate(data["tasks"]):
            status = "✅ Completed" if task.get("completed", False) else "🟡 Pending"
            st.write(
                f"**{task.get('title', 'Untitled')}** — {status}  \n"
                f"Subject: {task.get('subject', 'General')} · "
                f"Due: {task.get('due', 'Not set')}"
            )
    else:
        st.info("No tasks yet. Open Homework & Tasks to add your first task.")


# ---------------- PROFILE ----------------
elif page == "Student Profile":
    st.subheader("Student profile")
    st.write("Enter your details below.")

    with st.form("profile_form"):
        name = st.text_input("Student name", profile.get("name", ""))
        class_name = st.text_input("Class / Grade", profile.get("class", ""))
        school = st.text_input("School name", profile.get("school", ""))
        submitted = st.form_submit_button("Save profile")

    if submitted:
        profile["name"] = name.strip()
        profile["class"] = class_name.strip()
        profile["school"] = school.strip()
        if save_data():
            st.success("Profile saved!")


# ---------------- SUBJECTS ----------------
elif page == "Subjects":
    st.subheader("Subject manager")

    with st.form("subject_form", clear_on_submit=True):
        subject = st.text_input("Subject name")
        add_subject = st.form_submit_button("Add subject")

    if add_subject:
        subject = subject.strip()
        if not subject:
            st.error("Enter a subject name.")
        elif any(s.lower() == subject.lower() for s in data["subjects"]):
            st.warning("That subject already exists.")
        else:
            data["subjects"].append(subject)
            if save_data():
                st.success(f"{subject} added!")

    if data["subjects"]:
        st.write("### Your subjects")
        for i, subject in enumerate(data["subjects"]):
            col1, col2 = st.columns([5, 1])
            col1.write(f"{i + 1}. {subject}")
            if col2.button("Delete", key=f"subject_{i}"):
                data["subjects"].pop(i)
                refresh_saved_data()
    else:
        st.info("No subjects added yet.")


# ---------------- TASKS ----------------
elif page == "Homework & Tasks":
    st.subheader("Homework and tasks")

    with st.form("task_form", clear_on_submit=True):
        title = st.text_input("Task title")
        subject = st.text_input("Subject", value="General")
        due = st.text_input("Due date", placeholder="e.g. 12 October")
        add_task = st.form_submit_button("Add task")

    if add_task:
        if not title.strip():
            st.error("Enter a task title.")
        else:
            data["tasks"].append({
                "title": title.strip(),
                "subject": subject.strip() or "General",
                "due": due.strip() or "Not set",
                "completed": False
            })
            if save_data():
                st.success("Task added!")

    st.write("### Your tasks")
    if data["tasks"]:
        for i, task in enumerate(data["tasks"]):
            with st.container(border=True):
                col1, col2 = st.columns([4, 2])
                col1.write(f"**{task.get('title', 'Untitled')}**")
                col1.caption(
                    f"{task.get('subject', 'General')} · "
                    f"Due: {task.get('due', 'Not set')}"
                )
                done = task.get("completed", False)
                new_status = col2.checkbox(
                    "Completed",
                    value=done,
                    key=f"task_done_{i}"
                )

                button_col1, button_col2 = st.columns(2)
                if new_status != done:
                    task["completed"] = new_status
                    save_data()
                    st.rerun()

                if button_col1.button("Delete task", key=f"task_delete_{i}"):
                    data["tasks"].pop(i)
                    refresh_saved_data()
    else:
        st.info("No homework tasks yet.")


# ---------------- MARKS ----------------
elif page == "Marks & Results":
    st.subheader("Marks and results")

    with st.form("marks_form", clear_on_submit=True):
        subject = st.text_input("Subject")
        maximum = st.number_input("Maximum marks", min_value=1.0, value=100.0)
        mark = st.number_input("Marks obtained", min_value=0.0, max_value=maximum)
        add_mark = st.form_submit_button("Save marks")

    if add_mark:
        if not subject.strip():
            st.error("Enter a subject name.")
        else:
            data["marks"].append({
                "subject": subject.strip(),
                "mark": mark,
                "maximum": maximum
            })
            if save_data():
                st.success("Marks saved!")

    if data["marks"]:
        st.write("### Results")
        st.dataframe(data["marks"], use_container_width=True)

        total, maximum, percentage = results()
        a, b, c = st.columns(3)
        a.metric("Total marks", f"{total:g} / {maximum:g}")
        b.metric("Percentage", f"{percentage:.2f}%")
        c.metric("Grade", grade_for(percentage))

        for i, item in enumerate(data["marks"]):
            if st.button(f"Delete {item['subject']} entry", key=f"mark_delete_{i}"):
                data["marks"].pop(i)
                refresh_saved_data()
    else:
        st.info("Add your marks to calculate your percentage and grade.")


# ---------------- TIMETABLE ----------------
elif page == "Timetable":
    st.subheader("Class timetable")

    with st.form("timetable_form", clear_on_submit=True):
        day = st.selectbox(
            "Day",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        )
        time = st.text_input("Time", placeholder="e.g. 9:00–9:45 AM")
        subject = st.text_input("Subject")
        add_class = st.form_submit_button("Add class")

    if add_class:
        if not time.strip() or not subject.strip():
            st.error("Enter both time and subject.")
        else:
            data["timetable"].append({
                "day": day,
                "time": time.strip(),
                "subject": subject.strip()
            })
            if save_data():
                st.success("Timetable entry added!")

    if data["timetable"]:
        st.dataframe(data["timetable"], use_container_width=True)
        for i, item in enumerate(data["timetable"]):
            if st.button(
                f"Delete {item['day']} - {item['subject']}",
                key=f"class_delete_{i}"
            ):
                data["timetable"].pop(i)
                refresh_saved_data()
    else:
        st.info("Your timetable is empty.")


# ---------------- SEARCH ----------------
elif page == "Search":
    st.subheader("Search study information")
    query = st.text_input("Search by subject, task, day, or keyword").strip().lower()

    if query:
        found = []

        for subject in data["subjects"]:
            if query in subject.lower():
                found.append(("Subject", subject))

        for task in data["tasks"]:
            text = f"{task.get('title', '')} {task.get('subject', '')} {task.get('due', '')}"
            if query in text.lower():
                found.append(("Task", task.get("title", "Untitled")))

        for item in data["marks"]:
            if query in item.get("subject", "").lower():
                found.append(("Marks", item["subject"]))

        for item in data["timetable"]:
            text = f"{item.get('day', '')} {item.get('time', '')} {item.get('subject', '')}"
            if query in text.lower():
                found.append(("Timetable", f"{item['day']} — {item['time']} — {item['subject']}"))

        if found:
            for category, value in found:
                st.write(f"**{category}:** {value}")
        else:
            st.info("No matching information found.")


# ---------------- ABOUT ----------------
elif page == "About":
    st.subheader("About Student Life Assistant")
    st.write(
        "A student organiser built with Python and Streamlit. "
        "It helps manage a student profile, subjects, homework, marks, "
        "timetable, and academic progress."
    )
    st.write("Data is stored locally in student_data.json.")
    st.caption("This project does not require you to write HTML, CSS, or JavaScript.")

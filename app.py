import json
from pathlib import Path
from datetime import date
import streamlit as st

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "student_data.json"
DEFAULT = {
    "profile": {"name": "Student", "grade": "SSLC", "goal": "Learn something new every day"},
    "subjects": ["English", "Mathematics", "Science"],
    "tasks": [],
    "marks": [],
    "timetable": []
}

st.set_page_config(page_title="NOVA | Student Life", page_icon="🌑", layout="wide")

def load_data():
    if DATA_FILE.exists():
        try:
            saved = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            for k, v in DEFAULT.items():
                saved.setdefault(k, v.copy() if isinstance(v, dict) else list(v))
            return saved
        except (json.JSONDecodeError, OSError):
            pass
    return json.loads(json.dumps(DEFAULT))

if "data" not in st.session_state:
    st.session_state.data = load_data()
data = st.session_state.data

def save():
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def header(kicker, title, subtitle):
    st.caption(kicker.upper())
    st.title(title)
    st.write(subtitle)
    st.divider()

def metric(label, value, help_text):
    with st.container(border=True):
        st.caption(label.upper())
        st.markdown(f"## {value}")
        st.caption(help_text)

st.sidebar.markdown("# 🌑 NOVA")
st.sidebar.caption("STUDENT LIFE ASSISTANT")
st.sidebar.divider()
page = st.sidebar.radio("YOUR WORKSPACE", [
    "Overview", "My Tasks", "Subjects", "Marks & Results", "Timetable", "My Profile"
])
st.sidebar.divider()
st.sidebar.info("Plan with purpose. Learn at your pace.")
st.sidebar.caption("Python + Streamlit")

if page == "Overview":
    header("Your personal command center", "Welcome to your space. ✨",
           "A focused, calm workspace to organise school and celebrate progress.")
    tasks = data["tasks"]
    pending = [x for x in tasks if not x.get("done")]
    done = [x for x in tasks if x.get("done")]
    marks = data["marks"]
    avg = sum(x["mark"] for x in marks) / len(marks) if marks else 0
    a, b, c, d = st.columns(4)
    with a: metric("Subjects", len(data["subjects"]), "Your learning map")
    with b: metric("Open tasks", len(pending), "One step at a time")
    with c: metric("Completed", len(done), "Progress you've made")
    with d: metric("Mark average", f"{avg:.1f}%", "Across saved results" if marks else "Add your first result")
    left, right = st.columns([1.5, 1], gap="large")
    with left:
        st.subheader("⚡ Focus board")
        with st.container(border=True):
            todays = [x for x in pending if x.get("due") == date.today().isoformat()]
            if todays:
                for t in todays: st.write(f"• **{t['title']}**")
            elif pending:
                next_task = sorted(pending, key=lambda x: x.get("due") or "9999-12-31")[0]
                st.markdown(f"### {next_task['title']}")
                st.caption(f"Next due: {next_task.get('due') or 'No date set'}")
            else:
                st.write("Your task list is clear. Take a breath, or add a new task.")
            st.progress(len(done) / max(len(tasks), 1), text=f"{len(done)} of {len(tasks)} tasks completed" if tasks else "Your progress begins with your first task")
    with right:
        st.subheader("🎯 Current goal")
        with st.container(border=True):
            st.markdown(f"### {data['profile'].get('goal') or 'Choose a goal that matters to you.'}")
            st.caption(f"Keep going, {data['profile'].get('name') or 'student'}. Small steps count.")
        st.subheader("✨ Quick add")
        if st.button("＋ Create a task", type="primary", use_container_width=True):
            st.session_state.show_quick_task = True
        if st.session_state.get("show_quick_task"):
            with st.form("quick_task", clear_on_submit=True):
                title = st.text_input("Task name")
                due = st.date_input("Due date", value=date.today())
                priority = st.selectbox("Priority", ["Normal", "Important", "Urgent"])
                if st.form_submit_button("Save task"):
                    if title.strip():
                        data["tasks"].append({"title": title.strip(), "due": due.isoformat(), "priority": priority, "done": False})
                        save()
                        st.session_state.show_quick_task = False
                        st.rerun()
                    else: st.warning("Please enter a task name.")

elif page == "My Tasks":
    header("Plan • Do • Finish", "My Tasks", "Assignments, revision, and reminders — all in one place.")
    with st.expander("＋ Add a task", expanded=not bool(data["tasks"])):
        with st.form("task_add", clear_on_submit=True):
            title = st.text_input("Task or assignment", placeholder="e.g. Revise chapter 3")
            c1, c2 = st.columns(2)
            due = c1.date_input("Due date", value=date.today())
            priority = c2.selectbox("Priority", ["Normal", "Important", "Urgent"])
            note = st.text_input("Note (optional)")
            if st.form_submit_button("Add task", type="primary"):
                if title.strip():
                    data["tasks"].append({"title": title.strip(), "due": due.isoformat(), "priority": priority, "note": note, "done": False})
                    save(); st.rerun()
                else: st.warning("Enter a task name.")
    mode = st.segmented_control("Show", ["All", "Open", "Completed"], default="All")
    shown = [(i, t) for i, t in enumerate(data["tasks"]) if mode == "All" or (mode == "Open" and not t.get("done")) or (mode == "Completed" and t.get("done"))]
    if not shown: st.info("Nothing here yet. Add a task above.")
    for i, task in shown:
        with st.container(border=True):
            c1, c2, c3 = st.columns([0.08, 0.72, 0.2])
            checked = c1.checkbox("Done", value=task.get("done", False), key=f"done_{i}", label_visibility="collapsed")
            if checked != task.get("done", False):
                task["done"] = checked; save(); st.rerun()
            with c2:
                st.markdown(f"~~{task['title']}~~" if task.get("done") else f"**{task['title']}**")
                st.caption(f"Due {task.get('due') or 'no date'} · {task.get('priority', 'Normal')} priority")
                if task.get("note"): st.caption(task["note"])
            if c3.button("Delete", key=f"del_task_{i}"):
                data["tasks"].pop(i); save(); st.rerun()

elif page == "Subjects":
    header("Your learning map", "Subjects", "Keep your learning areas organised and easy to find.")
    with st.form("subject_add", clear_on_submit=True, border=True):
        name = st.text_input("Subject name", placeholder="e.g. Physics")
        if st.form_submit_button("＋ Add subject", type="primary"):
            if name.strip() and name.strip() not in data["subjects"]:
                data["subjects"].append(name.strip()); save(); st.rerun()
            else: st.warning("Enter a new subject name.")
    if data["subjects"]:
        cols = st.columns(3)
        for i, subject in enumerate(data["subjects"]):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown("### 📘 " + subject)
                    st.caption("Your learning, your progress.")
                    if st.button("Remove", key=f"subject_{i}"):
                        data["subjects"].pop(i); save(); st.rerun()
    else: st.info("Add your first subject above.")

elif page == "Marks & Results":
    header("Measure your learning", "Marks & Results", "Record results and notice your progress over time.")
    with st.form("mark_add", clear_on_submit=True, border=True):
        subjects = data["subjects"]
        c1, c2, c3 = st.columns(3)
        subject = c1.selectbox("Subject", subjects) if subjects else c1.text_input("Subject")
        exam = c2.text_input("Exam name", placeholder="Unit test")
        mark = c3.number_input("Mark (%)", min_value=0.0, max_value=100.0, step=1.0)
        if st.form_submit_button("Save result", type="primary"):
            if subject and exam.strip():
                data["marks"].append({"subject": subject, "exam": exam.strip(), "mark": mark, "date": date.today().isoformat()})
                save(); st.rerun()
            else: st.warning("Choose a subject and enter an exam name.")
    if data["marks"]:
        avg = sum(x["mark"] for x in data["marks"]) / len(data["marks"])
        st.metric("Average recorded mark", f"{avg:.1f}%")
        for i, item in enumerate(data["marks"]):
            with st.container(border=True):
                c1, c2, c3 = st.columns([0.55, 0.25, 0.2])
                c1.markdown(f"**{item['subject']}**")
                c1.caption(
                    f"{item.get('exam', 'Previous result')} · "
                    f"{item.get('date', 'Date not recorded')}"
                )
                mark = float(item.get("mark", 0))
                maximum = float(item.get("maximum", 100))
                percentage = (mark / maximum * 100) if maximum > 0 else 0
                c2.metric("Mark", f"{percentage:.1f}%")
                if c3.button("Delete", key=f"mark_{i}"):
                    data["marks"].pop(i); save(); st.rerun()
    else: st.info("Your results will appear here after your first entry.")

elif page == "Timetable":
    header("Make time for what matters", "Timetable", "Build a simple weekly plan for classes or study sessions.")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    with st.form("timetable_add", clear_on_submit=True, border=True):
        c1, c2, c3 = st.columns(3)
        day = c1.selectbox("Day", days)
        time = c2.text_input("Time", placeholder="09:00–09:45")
        subjects = data["subjects"] + ["Other"] if data["subjects"] else ["Other"]
        subject = c3.selectbox("Subject / activity", subjects)
        if st.form_submit_button("Add to timetable", type="primary"):
            if time.strip():
                data["timetable"].append({"day": day, "time": time.strip(), "subject": subject})
                save(); st.rerun()
            else: st.warning("Enter a time.")
    for day in days:
        entries = [x for x in data["timetable"] if x["day"] == day]
        if entries:
            with st.expander(f"📅 {day} · {len(entries)} item(s)", expanded=day == date.today().strftime("%A")):
                for i, item in enumerate(entries):
                    c1, c2, c3 = st.columns([0.25, 0.55, 0.2])
                    c1.write(item["time"]); c2.write(item["subject"])
                    if c3.button("Remove", key=f"tt_{day}_{i}"):
                        data["timetable"].remove(item); save(); st.rerun()
    if not data["timetable"]: st.info("Your timetable is empty. Add a study session above.")


elif page == "My Profile":
    header(
        "Make this space yours",
        "My Profile",
        "Personalise your workspace and choose a goal to guide your week."
    )
    p = data["profile"]

    with st.form("profile_save", border=True):
        name = st.text_input(
            "Name or nickname",
            value=p.get("name", "Student")
        )
        grade = st.text_input(
            "Class / grade",
            value=p.get("grade", p.get("class", "SSLC"))
        )
        goal = st.text_area(
            "Current goal",
            value=p.get("goal", "")
        )

        submitted = st.form_submit_button(
            "Save profile",
            type="primary"
        )

        if submitted:
            data["profile"] = {
                "name": name.strip() or "Student",
                "grade": grade.strip(),
                "goal": goal.strip()
            }
            save()
            st.success("Profile saved.")

    st.caption(
        "Privacy tip: do not enter passwords, ID numbers, "
        "or other sensitive personal information."
    )

    with st.expander("About NOVA"):
        st.write(
            "A student organiser built using Python and Streamlit."
        )
        st.warning(
            "Cloud file storage may not preserve changes permanently. "
            "Avoid entering private student information."
        )

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, DailyPlan

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Session state initialisation
# Think of st.session_state as a dictionary that survives page reruns.
# We only create each object ONCE (on the very first run); after that we
# reuse whatever is already stored in the "vault".
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None   # will become an Owner instance

if "pet" not in st.session_state:
    st.session_state.pet = None     # will become a Pet instance

if "tasks" not in st.session_state:
    st.session_state.tasks = []     # list of Task instances
elif st.session_state.tasks and isinstance(st.session_state.tasks[0], dict):
    # Clear stale dict-based tasks left over from the old starter code.
    st.session_state.tasks = []

# Map human-readable time labels to HH:MM strings the Scheduler expects.
# The backend's _hhmm_to_min() uses "HH:MM" format; passing "morning" would crash.
TIME_LABEL_TO_HHMM = {
    "morning":   "08:00",
    "afternoon": "13:00",
    "evening":   "18:00",
    "any":       None,
}

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Step 1 — Owner & pet profile
# ---------------------------------------------------------------------------
st.subheader("Step 1 — Set up your profile")

owner_name      = st.text_input("Owner name", value="Jordan")
available_time  = st.number_input("Time available today (minutes)", min_value=10, max_value=480, value=90)
pet_name        = st.text_input("Pet name", value="Mochi")
species         = st.selectbox("Species", ["dog", "cat", "other"])
pet_age         = st.number_input("Pet age (years)", min_value=0, max_value=30, value=2)

if st.button("Save profile"):
    # Pet() and Owner() are constructed from the form values.
    # owner.add_pet(pet) links them — this is the same method from pawpal_system.py.
    pet   = Pet(name=pet_name, species=species, age=int(pet_age))
    owner = Owner(name=owner_name, available_minutes=int(available_time))
    owner.add_pet(pet)   # <-- Owner.add_pet() from pawpal_system.py

    st.session_state.owner = owner
    st.session_state.pet   = pet
    st.session_state.tasks = []   # reset tasks whenever the profile changes
    st.success(f"Profile saved! {owner_name} + {pet_name} are ready.")

# Show a status badge so it's clear whether the vault has a profile yet
if st.session_state.owner:
    st.caption(
        f"Current profile: **{st.session_state.owner.name}** / "
        f"**{st.session_state.pet.name}** ({st.session_state.pet.species}, "
        f"age {st.session_state.pet.age}) — "
        f"{st.session_state.owner.available_minutes} min available"
    )
else:
    st.info("No profile saved yet. Fill in the fields above and click Save profile.")

st.divider()

# ---------------------------------------------------------------------------
# Step 2 — Add tasks
# ---------------------------------------------------------------------------
st.subheader("Step 2 — Add care tasks")

PRIORITY_MAP = {"low": 1, "medium": 3, "high": 5}

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_name = st.text_input("Task name", value="Morning walk")
with col2:
    category  = st.selectbox("Category", ["walk", "feed", "meds", "grooming", "enrichment"])
with col3:
    duration  = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col4:
    priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col5:
    preferred_time_label = st.selectbox("Preferred time", ["any", "morning", "afternoon", "evening"])

if st.button("Add task"):
    if st.session_state.pet is None:
        st.warning("Save a profile first before adding tasks.")
    else:
        # Convert the human-readable label ("morning") to the HH:MM format
        # that Scheduler._hhmm_to_min() and detect_conflicts() expect.
        hhmm = TIME_LABEL_TO_HHMM[preferred_time_label]

        task = Task(
            name=task_name,
            category=category,
            duration_minutes=int(duration),
            priority=PRIORITY_MAP[priority_label],
            preferred_time=hhmm,
        )
        # Pet.add_task() from pawpal_system.py — this is what stores the task
        # on the Pet object that the Scheduler will later read from.
        st.session_state.pet.add_task(task)   # <-- Pet.add_task()
        st.session_state.tasks.append(task)
        st.success(f"Added: {task_name} ({duration} min, priority {PRIORITY_MAP[priority_label]})")

# ---- Task list with sort/filter controls --------------------------------
if st.session_state.tasks:
    # Build a temporary Scheduler so we can use its sort/filter methods here.
    # This doesn't generate a schedule — it just gives us access to the methods
    # like sort_tasks_by_priority() and filter_by_status() from pawpal_system.py.
    _sched = Scheduler(st.session_state.owner)

    sort_col, filter_col = st.columns(2)
    with sort_col:
        sort_mode = st.radio(
            "Sort by", ["Priority (high → low)", "Time of day"],
            horizontal=True, label_visibility="collapsed"
        )
    with filter_col:
        show_filter = st.radio(
            "Show", ["All tasks", "Pending only", "Completed only"],
            horizontal=True, label_visibility="collapsed"
        )

    # Use Scheduler methods to sort — these are the Phase 3 backend methods.
    if sort_mode == "Priority (high → low)":
        display_tasks = _sched.sort_tasks_by_priority()   # <-- Scheduler.sort_tasks_by_priority()
    else:
        display_tasks = _sched.sort_by_time()             # <-- Scheduler.sort_by_time()

    # Apply status filter via Scheduler.filter_by_status().
    if show_filter == "Pending only":
        display_tasks = [t for t in display_tasks if not t.completed]
    elif show_filter == "Completed only":
        display_tasks = [t for t in display_tasks if t.completed]

    # Map HH:MM back to a readable label for display.
    HHMM_TO_LABEL = {v: k for k, v in TIME_LABEL_TO_HHMM.items() if v is not None}

    # Render as a structured table so columns are easy to scan.
    table_rows = []
    for task in display_tasks:
        time_display = HHMM_TO_LABEL.get(task.preferred_time, "any") if task.preferred_time else "any"
        priority_display = {1: "Low", 3: "Medium", 5: "High"}.get(task.priority, str(task.priority))
        status_display = "Done" if task.completed else "Pending"
        table_rows.append({
            "Task":      ("~~" + task.name + "~~") if task.completed else task.name,
            "Category":  task.category,
            "Duration":  f"{task.duration_minutes} min",
            "Priority":  priority_display,
            "Time":      time_display,
            "Status":    status_display,
        })

    st.table(table_rows)

    # Inline Done checkboxes (below the table, indexed to match session_state.tasks order).
    st.caption("Mark tasks complete:")
    for i, task in enumerate(st.session_state.tasks):
        done = st.checkbox(task.name, value=task.completed, key=f"task_done_{i}")
        if done and not task.completed:
            task.mark_complete()   # <-- Task.mark_complete()
            st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Step 3 — Generate schedule
# ---------------------------------------------------------------------------
st.subheader("Step 3 — Generate today's schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.warning("Save a profile first.")
    elif not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(st.session_state.owner)
        plan = scheduler.generate_schedule()   # <-- Scheduler.generate_schedule()

        # ---- Top-level summary ------------------------------------------
        if plan.unscheduled_tasks:
            st.warning(plan.get_summary())
        else:
            st.success(plan.get_summary())

        # ---- Conflict warnings — shown prominently so the owner can act --
        # detect_conflicts() flags tasks whose preferred windows overlap.
        # Each warning names the two tasks and their exact time windows so the
        # owner knows exactly which walks or feeding times to reschedule.
        if plan.warnings:
            st.error(
                f"**{len(plan.warnings)} scheduling conflict(s) detected — "
                "please adjust the preferred times below.**"
            )
            for warning in plan.warnings:
                st.warning(f"**Conflict:** {warning}")
            st.caption(
                "Tip: Go back to Step 2, remove the conflicting tasks, and re-add them "
                "with different preferred times. PawPal+ will schedule them back-to-back "
                "automatically, but the times shown may differ from what you requested."
            )

        # ---- Scheduled tasks — rich table with time slots ---------------
        if plan.scheduled_tasks:
            st.markdown("**Scheduled tasks**")

            def _min_to_ampm(minutes: int) -> str:
                """Convert minutes-from-midnight to a readable 12-hour string."""
                h, m = divmod(minutes, 60)
                suffix = "AM" if h < 12 else "PM"
                h12 = h % 12 or 12
                return f"{h12}:{m:02d} {suffix}"

            scheduled_rows = []
            for task in plan.scheduled_tasks:
                time_slot = (
                    f"{_min_to_ampm(task.start_min)} – {_min_to_ampm(task.end_min)}"
                    if task.start_min is not None else "—"
                )
                priority_label_display = {1: "Low", 3: "Medium", 5: "High"}.get(
                    task.priority, str(task.priority)
                )
                scheduled_rows.append({
                    "Time slot":  time_slot,
                    "Task":       task.name,
                    "Category":   task.category,
                    "Duration":   f"{task.duration_minutes} min",
                    "Priority":   priority_label_display,
                    "Done?":      "Yes" if task.completed else "No",
                })

            st.table(scheduled_rows)

        # ---- Unscheduled tasks — shown as a warning so they stand out ---
        if plan.unscheduled_tasks:
            skipped_names = ", ".join(t.name for t in plan.unscheduled_tasks)
            st.warning(
                f"**Not enough time for:** {skipped_names}. "
                f"Increase your available time in Step 1, or shorten/remove lower-priority tasks."
            )

        # ---- Why this plan? expander ------------------------------------
        with st.expander("Why this plan?"):
            st.text(plan.explanation)

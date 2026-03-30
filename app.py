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
    preferred_time = st.selectbox("Preferred time", ["any", "morning", "afternoon", "evening"])

if st.button("Add task"):
    if st.session_state.pet is None:
        st.warning("Save a profile first before adding tasks.")
    else:
        task = Task(
            name=task_name,
            category=category,
            duration_minutes=int(duration),
            priority=PRIORITY_MAP[priority_label],
            preferred_time=None if preferred_time == "any" else preferred_time,
        )
        # Pet.add_task() from pawpal_system.py — this is what stores the task
        # on the Pet object that the Scheduler will later read from.
        st.session_state.pet.add_task(task)   # <-- Pet.add_task()
        st.session_state.tasks.append(task)
        st.success(f"Added: {task_name} ({duration} min, priority {PRIORITY_MAP[priority_label]})")

if st.session_state.tasks:
    st.write("Current tasks:")
    for i, task in enumerate(st.session_state.tasks):
        col_check, col_info = st.columns([1, 9])
        with col_check:
            # Checkbox calls task.mark_complete() — the method from pawpal_system.py.
            # Streamlit re-renders the row immediately after the state change.
            done = st.checkbox("Done", value=task.completed, key=f"task_done_{i}")
            if done and not task.completed:
                task.mark_complete()   # <-- Task.mark_complete()
        with col_info:
            label = f"~~{task.name}~~" if task.completed else task.name
            st.markdown(
                f"{label} — {task.category}, {task.duration_minutes} min, "
                f"priority {task.priority}"
                + (f", {task.preferred_time}" if task.preferred_time else "")
            )
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
        plan = scheduler.generate_schedule()

        st.success(plan.get_summary())
        st.text(plan.display())

        with st.expander("Why this plan?"):
            st.text(plan.explanation)

from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Alex", available_minutes=90)

dog = Pet(name="Biscuit", species="Dog", age=3, breed="Golden Retriever")
cat = Pet(name="Mochi", species="Cat", age=5)

owner.add_pet(dog)
owner.add_pet(cat)

# --- Tasks added intentionally OUT OF ORDER to test sorting ---
dog.add_task(Task(name="Evening walk",    category="walk",       duration_minutes=20, priority=4, preferred_time="18:00"))
dog.add_task(Task(name="Flea medication", category="meds",       duration_minutes=5,  priority=5, preferred_time="09:30", recurrence="weekly", due_date="2026-03-29"))
dog.add_task(Task(name="Morning walk",    category="walk",       duration_minutes=30, priority=5, preferred_time="07:00", recurrence="daily",  due_date="2026-03-29"))

cat.add_task(Task(name="Playtime",        category="enrichment", duration_minutes=20, priority=2, preferred_time="19:00"))
cat.add_task(Task(name="Vet pill",        category="meds",       duration_minutes=5,  priority=5, preferred_time="08:00", recurrence="daily",  due_date="2026-03-29"))
cat.add_task(Task(name="Brush fur",       category="grooming",   duration_minutes=15, priority=3))  # no preferred_time

# --- Intentional conflict: both tasks claim 07:00, and Morning walk runs until 07:30 ---
dog.add_task(Task(name="Breakfast feed",  category="feed",       duration_minutes=10, priority=5, preferred_time="07:00"))

# --- Mark one task complete to test status filtering ---
dog.get_tasks()[0].mark_complete()  # Evening walk is done

# --- Show task lists BEFORE completing recurring tasks ---
print("=" * 40)
print("  BEFORE completing tasks")
print("=" * 40)
print("Biscuit's tasks:")
for task in dog._tasks:
    print(f"  - {task.name} | recurrence={task.recurrence} | due_date={task.due_date}")
print("Mochi's tasks:")
for task in cat._tasks:
    print(f"  - {task.name} | recurrence={task.recurrence} | due_date={task.due_date}")

# --- Generate and print schedule ---
scheduler = Scheduler(owner)
plan = scheduler.generate_schedule()

print()
print("=" * 40)
print("         TODAY'S SCHEDULE")
print("=" * 40)
print(plan.display())
print()
print(plan.get_summary())
print()
print("--- Reasoning ---")
print(plan.explanation)

# --- Complete recurring tasks and auto-schedule next occurrences ---
# Find Morning walk and Vet pill by name for clarity
morning_walk = next(t for t in dog._tasks if t.name == "Morning walk")
vet_pill = next(t for t in cat._tasks if t.name == "Vet pill")

scheduler.mark_task_complete(morning_walk)
scheduler.mark_task_complete(vet_pill)

# --- Show task lists AFTER completing recurring tasks ---
print()
print("=" * 40)
print("  AFTER completing tasks")
print("=" * 40)
print("Biscuit's tasks:")
for task in dog._tasks:
    status = "done" if task.completed else "pending"
    print(f"  - {task.name} | status={status} | recurrence={task.recurrence} | due_date={task.due_date}")
print("Mochi's tasks:")
for task in cat._tasks:
    status = "done" if task.completed else "pending"
    print(f"  - {task.name} | status={status} | recurrence={task.recurrence} | due_date={task.due_date}")

# --- Test sort_by_time ---
print()
print("=" * 40)
print("  TASKS SORTED BY TIME (chronological)")
print("=" * 40)
for task in scheduler.sort_by_time():
    time_label = task.preferred_time if task.preferred_time else "(no time set)"
    print(f"  {time_label:>10}  |  {task.name}")

# --- Test filter_by_status ---
print()
print("=" * 40)
print("  PENDING TASKS (not yet completed)")
print("=" * 40)
for task in scheduler.filter_by_status(completed=False):
    print(f"  o {task.name} — priority {task.priority}, {task.duration_minutes} min")

print()
print("=" * 40)
print("  COMPLETED TASKS")
print("=" * 40)
completed = scheduler.filter_by_status(completed=True)
if completed:
    for task in completed:
        print(f"  done {task.name}")
else:
    print("  (none yet)")

# --- Test filter_by_pet ---
print()
print("=" * 40)
print("  BISCUIT'S TASKS")
print("=" * 40)
for task in scheduler.filter_by_pet("Biscuit"):
    status = "done" if task.completed else "o"
    print(f"  {status} {task.name}")

print()
print("=" * 40)
print("  MOCHI'S TASKS")
print("=" * 40)
for task in scheduler.filter_by_pet("Mochi"):
    status = "done" if task.completed else "o"
    print(f"  {status} {task.name}")

from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Alex", available_minutes=90)

dog = Pet(name="Biscuit", species="Dog", age=3, breed="Golden Retriever")
cat = Pet(name="Mochi", species="Cat", age=5)

owner.add_pet(dog)
owner.add_pet(cat)

# --- Tasks for Biscuit ---
dog.add_task(Task(name="Morning walk",    category="walk",       duration_minutes=30, priority=5, preferred_time="morning"))
dog.add_task(Task(name="Evening walk",    category="walk",       duration_minutes=20, priority=4, preferred_time="evening"))
dog.add_task(Task(name="Flea medication", category="meds",       duration_minutes=5,  priority=5))

# --- Tasks for Mochi ---
cat.add_task(Task(name="Brush fur",       category="grooming",   duration_minutes=15, priority=3))
cat.add_task(Task(name="Playtime",        category="enrichment", duration_minutes=20, priority=2, preferred_time="evening"))
cat.add_task(Task(name="Vet pill",        category="meds",       duration_minutes=5,  priority=5))

# --- Generate and print schedule ---
scheduler = Scheduler(owner)
plan = scheduler.generate_schedule()

print("=" * 40)
print("         TODAY'S SCHEDULE")
print("=" * 40)
print(plan.display())
print()
print(plan.get_summary())
print()
print("--- Reasoning ---")
print(plan.explanation)

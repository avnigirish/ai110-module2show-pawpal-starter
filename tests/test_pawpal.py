from pawpal_system import Task, Pet, Owner, Scheduler


def test_mark_complete_changes_status():
    task = Task(name="Morning walk", category="walk", duration_minutes=30, priority=4)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="Dog", age=3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(name="Feed", category="feed", duration_minutes=10, priority=3))
    assert len(pet.get_tasks()) == 1
    pet.add_task(Task(name="Walk", category="walk", duration_minutes=20, priority=4))
    assert len(pet.get_tasks()) == 2


# --- Sorting correctness ---

def test_sort_by_time_chronological_order():
    """Tasks with explicit preferred_time should come back in HH:MM ascending order."""
    pet = Pet(name="Mochi", species="Cat", age=2)
    pet.add_task(Task(name="Evening meds",  category="meds",  duration_minutes=5,  priority=3, preferred_time="18:00"))
    pet.add_task(Task(name="Morning feed",  category="feed",  duration_minutes=10, priority=3, preferred_time="07:30"))
    pet.add_task(Task(name="Midday walk",   category="walk",  duration_minutes=20, priority=3, preferred_time="12:00"))

    owner = Owner(name="Alex", available_minutes=120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    sorted_tasks = scheduler.sort_by_time()
    times = [t.preferred_time for t in sorted_tasks]
    assert times == ["07:30", "12:00", "18:00"]


def test_sort_by_time_none_times_last():
    """Tasks with no preferred_time should sort after all timed tasks."""
    pet = Pet(name="Mochi", species="Cat", age=2)
    pet.add_task(Task(name="Flexible task", category="enrichment", duration_minutes=15, priority=2))
    pet.add_task(Task(name="Morning feed",  category="feed",       duration_minutes=10, priority=3, preferred_time="08:00"))

    owner = Owner(name="Alex", available_minutes=120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    sorted_tasks = scheduler.sort_by_time()
    assert sorted_tasks[0].preferred_time == "08:00"
    assert sorted_tasks[-1].preferred_time is None


# --- Recurrence logic ---

def test_daily_recurrence_advances_one_day():
    """Completing a daily task should produce a new task due the following day."""
    task = Task(
        name="Daily walk",
        category="walk",
        duration_minutes=30,
        priority=4,
        recurrence="daily",
        due_date="2026-03-29",
    )
    next_task = task.next_occurrence()
    assert next_task is not None
    assert next_task.due_date == "2026-03-30"
    assert next_task.completed is False


def test_weekly_recurrence_advances_seven_days():
    """Completing a weekly task should produce a new task due 7 days later."""
    task = Task(
        name="Weekly grooming",
        category="grooming",
        duration_minutes=60,
        priority=3,
        recurrence="weekly",
        due_date="2026-03-29",
    )
    next_task = task.next_occurrence()
    assert next_task is not None
    assert next_task.due_date == "2026-04-05"


def test_mark_task_complete_adds_recurrence_to_pet():
    """mark_task_complete should append the next occurrence to the pet's task list."""
    pet = Pet(name="Biscuit", species="Dog", age=3)
    task = Task(
        name="Daily walk",
        category="walk",
        duration_minutes=30,
        priority=4,
        recurrence="daily",
        due_date="2026-03-29",
    )
    pet.add_task(task)

    owner = Owner(name="Alex", available_minutes=120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    next_task = scheduler.mark_task_complete(task)

    assert task.completed is True
    assert next_task is not None
    assert next_task in pet.get_tasks()
    assert next_task.due_date == "2026-03-30"


def test_non_recurring_task_returns_none():
    """next_occurrence on a task with no recurrence should return None."""
    task = Task(name="One-time vet visit", category="meds", duration_minutes=60, priority=5)
    assert task.next_occurrence() is None


# --- Conflict detection ---

def test_conflict_detected_for_same_time():
    """Two tasks requesting the exact same start time should produce a conflict warning."""
    pet = Pet(name="Biscuit", species="Dog", age=3)
    pet.add_task(Task(name="Feed",     category="feed", duration_minutes=10, priority=3, preferred_time="08:00"))
    pet.add_task(Task(name="Morning walk", category="walk", duration_minutes=30, priority=4, preferred_time="08:00"))

    owner = Owner(name="Alex", available_minutes=120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_conflicts(pet.get_tasks())
    assert len(warnings) == 1
    assert "Feed" in warnings[0]
    assert "Morning walk" in warnings[0]


def test_no_conflict_for_sequential_tasks():
    """Tasks that end before the next one starts should produce no warnings."""
    pet = Pet(name="Biscuit", species="Dog", age=3)
    pet.add_task(Task(name="Feed",     category="feed", duration_minutes=10, priority=3, preferred_time="08:00"))
    pet.add_task(Task(name="Walk",     category="walk", duration_minutes=30, priority=4, preferred_time="08:30"))

    owner = Owner(name="Alex", available_minutes=120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_conflicts(pet.get_tasks())
    assert warnings == []


def test_no_conflict_for_tasks_without_preferred_time():
    """Flexible tasks (no preferred_time) should never be flagged as conflicts."""
    pet = Pet(name="Mochi", species="Cat", age=2)
    pet.add_task(Task(name="Play",  category="enrichment", duration_minutes=20, priority=2))
    pet.add_task(Task(name="Brush", category="grooming",   duration_minutes=15, priority=2))

    owner = Owner(name="Alex", available_minutes=120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_conflicts(pet.get_tasks())
    assert warnings == []

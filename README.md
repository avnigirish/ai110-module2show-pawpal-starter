# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

Beyond the core priority-based planner, PawPal+ includes several logic improvements that make the scheduler more useful for real pet owners:

**Sorting**
- `sort_by_time()` — orders all tasks chronologically by `preferred_time` (`HH:MM` strings). Tasks without a time preference sort to the end. Uses a two-part lambda key so no datetime parsing is needed.

**Filtering**
- `filter_by_status(completed)` — returns only pending or only completed tasks across all pets, making it easy to see what still needs to be done today.
- `filter_by_pet(name)` — returns the task list for a single named pet, useful when an owner manages multiple animals.

**Recurring tasks**
- Tasks support a `recurrence` field (`"daily"` or `"weekly"`) and a `due_date`.
- `Scheduler.mark_task_complete(task)` marks the task done and automatically appends the next occurrence (date calculated with `timedelta`) to the same pet's task list — no manual re-entry required.

**Conflict detection**
- `detect_conflicts(tasks)` checks every unique pair of scheduled tasks (via `itertools.combinations`) for overlapping `preferred_time` windows using the standard interval-overlap test: `a_start < b_end AND b_start < a_end`.
- Conflicts are surfaced as plain warning strings in the `DailyPlan` output — the scheduler never crashes on a conflict.
- Only tasks with an explicit `preferred_time` are checked; flexible tasks (no time set) are intentionally excluded to avoid noise.

---

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

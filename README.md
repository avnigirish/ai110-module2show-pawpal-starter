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

## Testing PawPal+

### Run the test suite

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

| Area | Tests | What is verified |
|---|---|---|
| **Sorting** | `test_sort_by_time_chronological_order`, `test_sort_by_time_none_times_last` | Tasks with `preferred_time` are returned in ascending HH:MM order; tasks with no time sort last |
| **Recurrence** | `test_daily_recurrence_advances_one_day`, `test_weekly_recurrence_advances_seven_days`, `test_mark_task_complete_adds_recurrence_to_pet`, `test_non_recurring_task_returns_none` | Daily tasks advance 1 day, weekly tasks advance 7 days, the new occurrence is appended to the correct pet, and non-recurring tasks return `None` |
| **Conflict detection** | `test_conflict_detected_for_same_time`, `test_no_conflict_for_sequential_tasks`, `test_no_conflict_for_tasks_without_preferred_time` | Overlapping `preferred_time` windows produce a warning; sequential and flexible tasks produce none |
| **Core model** | `test_mark_complete_changes_status`, `test_add_task_increases_pet_task_count` | `Task.mark_complete()` flips the flag; `Pet.add_task()` grows the task list |

### Confidence Level

**4 / 5 stars**

The scheduler's sorting, recurrence, and conflict-detection logic is well-covered and all 11 tests pass. One star is held back because `generate_schedule` (the full greedy planner end-to-end, including time-budget exhaustion and the Streamlit UI layer) does not yet have dedicated tests.

---

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

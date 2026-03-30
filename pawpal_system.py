from dataclasses import dataclass, field
from datetime import date as Date, timedelta
from itertools import combinations
from typing import Optional


@dataclass
class Task:
    name: str
    category: str  # e.g. "walk", "feed", "meds", "grooming", "enrichment"
    duration_minutes: int
    priority: int  # 1–5, where 5 is most urgent
    preferred_time: Optional[str] = None  # e.g. "morning", "evening"
    completed: bool = False
    recurrence: Optional[str] = None   # "daily", "weekly", or None
    due_date: Optional[str] = None     # ISO date string, e.g. "2026-03-29"
    start_min: Optional[int] = None    # assigned start time in minutes from midnight
    end_min: Optional[int] = None      # assigned end time in minutes from midnight

    def update(self, **kwargs):
        """Update one or more task attributes by keyword; raises AttributeError for unknown fields."""
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise AttributeError(f"Task has no attribute '{key}'")
            setattr(self, key, value)

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """Return a new Task for the next recurrence, or None if not recurring."""
        if self.recurrence is None:
            return None

        if self.due_date is not None:
            base_date = Date.fromisoformat(self.due_date)
        else:
            base_date = Date.today()

        if self.recurrence == "daily":
            next_date = base_date + timedelta(days=1)
        elif self.recurrence == "weekly":
            next_date = base_date + timedelta(weeks=1)
        else:
            return None

        return Task(
            name=self.name,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            preferred_time=self.preferred_time,
            completed=False,
            recurrence=self.recurrence,
            due_date=next_date.isoformat(),
        )


@dataclass
class Pet:
    name: str
    species: str
    age: int
    breed: Optional[str] = None
    _tasks: list = field(default_factory=list, repr=False)

    def add_task(self, task: Task):
        """Add a care task to this pet's task list."""
        self._tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a task from this pet's task list; raises ValueError if not found."""
        self._tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self._tasks)


class Owner:
    def __init__(self, name: str, available_minutes: int):
        self.name = name
        self.available_minutes = available_minutes
        self._pets: list[Pet] = []

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's pet list."""
        self._pets.append(pet)

    def get_pet(self) -> Optional[Pet]:
        """Returns the first pet, for single-pet convenience."""
        return self._pets[0] if self._pets else None

    def get_pets(self) -> list[Pet]:
        """Return a copy of the owner's pet list."""
        return list(self._pets)

    def get_all_tasks(self) -> list[Task]:
        """Aggregates tasks across all pets — primary entry point for Scheduler."""
        tasks = []
        for pet in self._pets:
            tasks.extend(pet.get_tasks())
        return tasks


@dataclass
class DailyPlan:
    date: str
    scheduled_tasks: list = field(default_factory=list)
    unscheduled_tasks: list = field(default_factory=list)
    explanation: str = ""
    warnings: list = field(default_factory=list)

    def display(self) -> str:
        """Render the plan as a formatted text block with scheduled and skipped tasks."""
        lines = [f"Daily Plan — {self.date}", "=" * 35]
        if self.scheduled_tasks:
            lines.append("Scheduled:")
            for task in self.scheduled_tasks:
                status = "✓" if task.completed else "○"
                lines.append(
                    f"  {status} {task.name} ({task.duration_minutes} min, priority {task.priority})"
                )
        if self.unscheduled_tasks:
            lines.append("\nCould not fit:")
            for task in self.unscheduled_tasks:
                lines.append(f"  - {task.name} ({task.duration_minutes} min)")
        if self.warnings:
            lines.append("\nConflict warnings:")
            for w in self.warnings:
                lines.append(f"  ⚠ {w}")
        return "\n".join(lines)

    def get_summary(self) -> str:
        """Return a one-line summary of how many tasks were scheduled vs skipped."""
        total = len(self.scheduled_tasks) + len(self.unscheduled_tasks)
        skipped = len(self.unscheduled_tasks)
        return (
            f"{len(self.scheduled_tasks)} of {total} tasks scheduled. "
            + (f"{skipped} skipped due to time constraints." if skipped else "All tasks fit!")
        )


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def sort_tasks_by_priority(self) -> list[Task]:
        """Returns all tasks across owner's pets sorted highest priority first."""
        return sorted(self.owner.get_all_tasks(), key=lambda t: t.priority, reverse=True)

    def sort_by_time(self) -> list[Task]:
        """Return all tasks across the owner's pets sorted chronologically by preferred_time.

        Sorting key: a two-element tuple (is_none, time_str). Tasks with a preferred_time
        of None sort last because (True, "") > (False, "HH:MM"). HH:MM strings sort
        lexicographically, which is identical to chronological order, so no datetime
        parsing is needed.

        Returns:
            A new list of Task objects in ascending time order, unset times at the end.
        """
        return sorted(
            self.owner.get_all_tasks(),
            key=lambda t: (t.preferred_time is None, t.preferred_time or "")
        )

    def filter_by_status(self, completed: bool) -> list[Task]:
        """Return all tasks across the owner's pets filtered by completion status.

        Args:
            completed: Pass True to get finished tasks, False to get pending tasks.

        Returns:
            A new list containing only tasks whose completed flag matches the argument.
        """
        return [t for t in self.owner.get_all_tasks() if t.completed == completed]

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return the task list for a single named pet.

        Args:
            pet_name: The pet's name; matched case-insensitively.

        Returns:
            A copy of that pet's task list, or an empty list if no pet by that name exists.
        """
        for pet in self.owner.get_pets():
            if pet.name.lower() == pet_name.lower():
                return pet.get_tasks()
        return []

    @staticmethod
    def _hhmm_to_min(hhmm: str) -> int:
        """Convert a 'HH:MM' string to an integer count of minutes from midnight.

        Example: '07:30' -> 450, '18:00' -> 1080.

        Args:
            hhmm: A time string in 'HH:MM' 24-hour format.

        Returns:
            Total minutes elapsed since midnight.
        """
        h, m = hhmm.split(":")
        return int(h) * 60 + int(m)

    def _assign_times(self, tasks: list[Task], default_start: int = 480) -> None:
        """Assign concrete start_min and end_min to each task using a forward-moving cursor.

        The cursor starts at default_start (08:00 by default). For each task:
        - If preferred_time is set, the cursor snaps forward to that time if it hasn't
          passed yet; otherwise the cursor stays where it is (tasks never go backward).
        - start_min is set to the current cursor position; end_min = start_min + duration.
        - The cursor advances to end_min before the next task.

        This method mutates the tasks in-place and returns None.

        Args:
            tasks: Ordered list of Task objects to assign times to.
            default_start: Starting cursor position in minutes from midnight (default 480 = 08:00).
        """
        cursor = default_start
        for task in tasks:
            if task.preferred_time:
                preferred = self._hhmm_to_min(task.preferred_time)
                cursor = max(cursor, preferred)
            task.start_min = cursor
            task.end_min = cursor + task.duration_minutes
            cursor = task.end_min

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Detect scheduling conflicts among tasks that have an explicit preferred_time.

        Builds a time interval [preferred_time, preferred_time + duration) for every task
        that has preferred_time set, then checks every unique pair with the standard
        interval-overlap test: two intervals [a_s, a_e) and [b_s, b_e) overlap when
        a_s < b_e AND b_s < a_e.

        Uses itertools.combinations to enumerate all unique pairs without index arithmetic.
        Uses the *requested* preferred_time (not cursor-adjusted slots from _assign_times)
        so that two tasks both claiming the same hour are always flagged, even if the
        cursor would have resolved the collision silently.

        Tasks without a preferred_time are never flagged — they are flexible by design.

        Args:
            tasks: The list of scheduled tasks to check (typically plan.scheduled_tasks).

        Returns:
            A list of human-readable warning strings, one per overlapping pair.
            Returns an empty list if no conflicts are found. Never raises an exception.
        """
        # Build (start, end, task) only for tasks with an explicit preferred_time
        timed = [
            (self._hhmm_to_min(t.preferred_time), self._hhmm_to_min(t.preferred_time) + t.duration_minutes, t)
            for t in tasks if t.preferred_time
        ]
        warnings = []
        # combinations(timed, 2) yields every unique pair — no index arithmetic needed
        for (a_s, a_e, a), (b_s, b_e, b) in combinations(timed, 2):
            # Overlap when one interval starts before the other ends
            if a_s < b_e and b_s < a_e:
                warnings.append(
                    f'"{a.name}" requested {a_s//60:02d}:{a_s%60:02d}–'
                    f'{a_e//60:02d}:{a_e%60:02d} overlaps with '
                    f'"{b.name}" requested {b_s//60:02d}:{b_s%60:02d}–'
                    f'{b_e//60:02d}:{b_e%60:02d}'
                )
        return warnings

    def generate_schedule(self) -> DailyPlan:
        """Greedy scheduler: fits tasks in priority order within the owner's time budget."""
        plan = DailyPlan(date=Date.today().isoformat())
        time_remaining = self.owner.available_minutes

        for task in self.sort_tasks_by_priority():
            if task.duration_minutes <= time_remaining:
                plan.scheduled_tasks.append(task)
                time_remaining -= task.duration_minutes
            else:
                plan.unscheduled_tasks.append(task)

        self._assign_times(plan.scheduled_tasks)
        plan.warnings = self.detect_conflicts(plan.scheduled_tasks)
        plan.explanation = self.explain_plan(plan)
        return plan

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Mark a task as complete and automatically queue its next occurrence if it recurs.

        Calls task.mark_complete(), then task.next_occurrence(). If a next occurrence is
        produced, locates the pet that owns the original task (via identity check against
        pet._tasks) and appends the new Task to that pet's list.

        Args:
            task: The Task to complete. Must belong to one of the owner's pets.

        Returns:
            The newly created next-occurrence Task, or None if the task does not recur.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            for pet in self.owner.get_pets():
                if task in pet._tasks:
                    pet.add_task(next_task)
                    break
        return next_task

    def explain_plan(self, plan: DailyPlan) -> str:
        """Build a human-readable explanation of why each task was scheduled or skipped."""
        lines = [
            f"{self.owner.name} has {self.owner.available_minutes} min available today.",
            f"{len(plan.scheduled_tasks)} task(s) scheduled in priority order:",
        ]
        for task in plan.scheduled_tasks:
            lines.append(f"  - {task.name} (priority {task.priority}, {task.duration_minutes} min)")
        if plan.unscheduled_tasks:
            lines.append(f"{len(plan.unscheduled_tasks)} task(s) skipped — not enough time remaining:")
            for task in plan.unscheduled_tasks:
                lines.append(f"  - {task.name} ({task.duration_minutes} min)")
        return "\n".join(lines)

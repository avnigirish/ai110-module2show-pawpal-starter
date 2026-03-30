from dataclasses import dataclass, field
from datetime import date as Date
from typing import Optional


@dataclass
class Task:
    name: str
    category: str  # e.g. "walk", "feed", "meds", "grooming", "enrichment"
    duration_minutes: int
    priority: int  # 1–5, where 5 is most urgent
    preferred_time: Optional[str] = None  # e.g. "morning", "evening"
    completed: bool = False

    def update(self, **kwargs):
        """Update one or more task attributes by keyword; raises AttributeError for unknown fields."""
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise AttributeError(f"Task has no attribute '{key}'")
            setattr(self, key, value)

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True


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

        plan.explanation = self.explain_plan(plan)
        return plan

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

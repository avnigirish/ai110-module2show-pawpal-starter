from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    name: str
    category: str  # e.g. "walk", "feed", "meds", "grooming", "enrichment"
    duration_minutes: int
    priority: int  # 1–5, where 5 is most urgent
    preferred_time: Optional[str] = None  # e.g. "morning", "evening"

    def update(self, **kwargs):
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    breed: Optional[str] = None
    _tasks: list = field(default_factory=list, repr=False)

    def add_task(self, task: Task):
        pass

    def remove_task(self, task: Task):
        pass

    def get_tasks(self) -> list[Task]:
        pass


class Owner:
    def __init__(self, name: str, available_minutes: int):
        self.name = name
        self.available_minutes = available_minutes
        self._pet: Optional[Pet] = None

    def add_pet(self, pet: Pet):
        pass

    def get_pet(self) -> Optional[Pet]:
        pass


@dataclass
class DailyPlan:
    date: str
    scheduled_tasks: list = field(default_factory=list)
    unscheduled_tasks: list = field(default_factory=list)
    explanation: str = ""

    def display(self) -> str:
        pass

    def get_summary(self) -> str:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet

    def sort_tasks_by_priority(self) -> list[Task]:
        pass

    def generate_schedule(self) -> DailyPlan:
        pass

    def explain_plan(self, plan: DailyPlan) -> str:
        pass

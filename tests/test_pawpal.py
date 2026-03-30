from pawpal_system import Task, Pet


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

from workout_bot.data_model.workout_plans import WorkoutPlans
from workout_bot.data_model.workout_plans import WorkoutTable


def test_():
    table = WorkoutTable("table_id", "table_name", {})
    workout_plans = WorkoutPlans()
    workout_plans.update_workout_table(table)

    assert workout_plans.is_table_id_present("table_id")
    assert not workout_plans.is_table_id_present("not_present")


def test_workout_plans_not_found():
    workout_plans = WorkoutPlans()

    plans = workout_plans.get_plan_names("not_present")

    assert not plans


def test_workout_plans_found():
    table = WorkoutTable("table_id", "table_name", {"page1": [], "page2": []})
    workout_plans = WorkoutPlans()
    workout_plans.update_workout_table(table)

    plans = workout_plans.get_plan_names("table_id")

    assert len(plans) == 2
    assert "page1" in plans
    assert "page2" in plans

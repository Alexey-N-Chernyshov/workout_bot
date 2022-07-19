from dataclasses import dataclass


@dataclass
class UserContext:
    current_plan: str
    current_week: int
    current_workout: int

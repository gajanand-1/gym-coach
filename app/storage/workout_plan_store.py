from typing import Optional
from sqlalchemy.orm import Session
from app.models.workout_plan import WorkoutPlan


class WorkoutPlanStore:
    def __init__(self, db: Session):
        self.db = db

    def save_plan(
        self,
        user_id: int,
        plan_data: dict,
        split_type: str,
        raw_response: str = "",
        plan_name: str = "Weekly Workout Plan",
    ) -> WorkoutPlan:
        (
            self.db.query(WorkoutPlan)
            .filter(WorkoutPlan.user_id == user_id, WorkoutPlan.is_active == True)  # noqa: E712
            .update({"is_active": False})
        )

        plan = WorkoutPlan(
            user_id=user_id,
            plan_data=plan_data,
            split_type=split_type,
            raw_response=raw_response,
            plan_name=plan_name,
            is_active=True,
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def get_active(self, user_id: int) -> Optional[WorkoutPlan]:
        return (
            self.db.query(WorkoutPlan)
            .filter(WorkoutPlan.user_id == user_id, WorkoutPlan.is_active == True)  # noqa: E712
            .order_by(WorkoutPlan.created_at.desc())
            .first()
        )

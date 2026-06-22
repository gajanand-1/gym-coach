from typing import Optional
from sqlalchemy.orm import Session
from app.models.diet_plan import DietPlan


class DietStore:
    def __init__(self, db: Session):
        self.db = db

    def save_plan(
        self,
        user_id: int,
        plan_data: dict,
        target_calories: int,
        target_protein: int,
        raw_response: str = "",
        week_start: str = "",
        plan_name: str = "Weekly Meal Plan",
    ) -> DietPlan:
        # Deactivate previous plans
        (
            self.db.query(DietPlan)
            .filter(DietPlan.user_id == user_id, DietPlan.is_active == True)  # noqa: E712
            .update({"is_active": False})
        )

        plan = DietPlan(
            user_id=user_id,
            plan_data=plan_data,
            target_calories=target_calories,
            target_protein=target_protein,
            raw_response=raw_response,
            week_start=week_start,
            plan_name=plan_name,
            is_active=True,
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def get_active(self, user_id: int) -> Optional[DietPlan]:
        return (
            self.db.query(DietPlan)
            .filter(DietPlan.user_id == user_id, DietPlan.is_active == True)  # noqa: E712
            .order_by(DietPlan.created_at.desc())
            .first()
        )

    def get_all(self, user_id: int) -> list:
        return (
            self.db.query(DietPlan)
            .filter(DietPlan.user_id == user_id)
            .order_by(DietPlan.created_at.desc())
            .all()
        )

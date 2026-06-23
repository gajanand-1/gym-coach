from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.grocery_plan import GroceryPlan


class GroceryStore:
    def __init__(self, db: Session):
        self.db = db

    def save_plan(
        self,
        user_id: int,
        items: List[Dict[str, Any]],
        diet_plan_id: Optional[int] = None,
        week_start: str = "",
    ) -> GroceryPlan:
        (
            self.db.query(GroceryPlan)
            .filter(GroceryPlan.user_id == user_id, GroceryPlan.is_active == True)  # noqa: E712
            .update({"is_active": False})
        )

        plan = GroceryPlan(
            user_id=user_id,
            items=items,
            diet_plan_id=diet_plan_id,
            week_start=week_start,
            is_active=True,
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def get_active(self, user_id: int) -> Optional[GroceryPlan]:
        return (
            self.db.query(GroceryPlan)
            .filter(GroceryPlan.user_id == user_id, GroceryPlan.is_active == True)  # noqa: E712
            .order_by(GroceryPlan.created_at.desc())
            .first()
        )

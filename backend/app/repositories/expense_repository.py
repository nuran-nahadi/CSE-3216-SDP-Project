from __future__ import annotations

import json
from datetime import datetime
from typing import Iterable, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, extract, func
from sqlalchemy.orm import Session

from app.models.models import Expense
from app.repositories.base import BaseRepository
from app.schemas.expenses import ExpenseCreate


class ExpenseRepository(BaseRepository[Expense]):
    """Data access helpers for expense resources."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Expense)

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------
    def list_expenses(
        self,
        user_id: UUID,
        *,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> Tuple[List[Expense], int]:
        query = self._filtered_query(
            user_id,
            start_date=start_date,
            end_date=end_date,
            category=category,
            min_amount=min_amount,
            max_amount=max_amount,
            search=search,
        )

        total = query.count()
        expenses = (
            query.order_by(desc(self.model.date))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        return expenses, total

    def create_expense(self, user_id: UUID, data: "ExpenseCreate") -> Expense:
        tags_json = json.dumps(data.tags) if getattr(data, "tags", None) else None
        expense = self.model(
            user_id=user_id,
            amount=data.amount,
            currency=data.currency,
            category=data.category,
            subcategory=data.subcategory,
            merchant=data.merchant,
            description=data.description,
            date=data.date,
            payment_method=data.payment_method,
            is_recurring=data.is_recurring,
            recurrence_rule=data.recurrence_rule,
            tags=tags_json,
        )
        self.db.add(expense)
        self.commit()
        self.refresh(expense)
        return expense

    def get_expense_for_user(self, expense_id: UUID, user_id: UUID) -> Optional[Expense]:
        return (
            self.db.query(self.model)
            .filter(and_(self.model.id == expense_id, self.model.user_id == user_id))
            .first()
        )

    def update_expense(self, expense: Expense, update_data: dict) -> Expense:
        if "tags" in update_data:
            update_data["tags"] = (
                json.dumps(update_data["tags"])
                if update_data["tags"]
                else None
            )
        for field, value in update_data.items():
            setattr(expense, field, value)
        self.commit()
        self.refresh(expense)
        return expense

    def delete_expense(self, expense: Expense) -> None:
        self.db.delete(expense)
        self.commit()

    def set_receipt_url(self, expense: Expense, receipt_url: str) -> Expense:
        expense.receipt_url = receipt_url
        self.commit()
        self.refresh(expense)
        return expense

    def get_recurring_expenses(self, user_id: UUID) -> List[Expense]:
        return (
            self.db.query(self.model)
            .filter(and_(self.model.user_id == user_id, self.model.is_recurring.is_(True)))
            .order_by(desc(self.model.date))
            .all()
        )

    def list_for_export(
        self,
        user_id: UUID,
        *,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Expense]:
        query = self._filtered_query(user_id, start_date=start_date, end_date=end_date)
        return query.order_by(desc(self.model.date)).all()

    # ------------------------------------------------------------------
    # Aggregation helpers
    # ------------------------------------------------------------------
    def list_in_period(
        self,
        user_id: UUID,
        *,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Expense]:
        query = self._filtered_query(user_id, start_date=start_date, end_date=end_date)
        return query.all()

    def get_category_totals(self, user_id: UUID) -> Iterable:
        return (
            self.db.query(
                self.model.category,
                func.sum(self.model.amount).label("total_amount"),
                func.count(self.model.id).label("count"),
            )
            .filter(self.model.user_id == user_id)
            .group_by(self.model.category)
            .all()
        )

    def get_category_totals_in_period(
        self,
        user_id: UUID,
        *,
        start_date: datetime,
        end_date: datetime,
    ) -> Iterable:
        return (
            self.db.query(
                self.model.category,
                func.sum(self.model.amount).label("total_amount"),
                func.count(self.model.id).label("count"),
            )
            .filter(
                and_(
                    self.model.user_id == user_id,
                    self.model.date >= start_date,
                    self.model.date <= end_date,
                )
            )
            .group_by(self.model.category)
            .all()
        )

    def get_monthly_expenses(self, user_id: UUID, year: int, month: int) -> List[Expense]:
        return (
            self.db.query(self.model)
            .filter(
                and_(
                    self.model.user_id == user_id,
                    extract("year", self.model.date) == year,
                    extract("month", self.model.date) == month,
                )
            )
            .all()
        )

    def sum_in_period(
        self,
        user_id: UUID,
        *,
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        total = (
            self.db.query(func.sum(self.model.amount))
            .filter(
                and_(
                    self.model.user_id == user_id,
                    self.model.date >= start_date,
                    self.model.date <= end_date,
                )
            )
            .scalar()
        )
        return float(total or 0)

    def get_monthly_category_totals(
        self,
        user_id: UUID,
        *,
        start_date: datetime,
        end_date: datetime,
    ) -> Iterable:
        return (
            self.db.query(
                extract("year", self.model.date).label("year"),
                extract("month", self.model.date).label("month"),
                self.model.category,
                func.sum(self.model.amount).label("total_amount"),
            )
            .filter(
                and_(
                    self.model.user_id == user_id,
                    self.model.date >= start_date,
                    self.model.date < end_date,
                )
            )
            .group_by("year", "month", self.model.category)
            .all()
        )

    def get_expenses_since(self, user_id: UUID, start_date: datetime) -> List[Expense]:
        return (
            self.db.query(self.model)
            .filter(and_(self.model.user_id == user_id, self.model.date >= start_date))
            .all()
        )

    def get_top_transactions(
        self,
        user_id: UUID,
        *,
        start_date: datetime,
        limit: int,
    ) -> List[Expense]:
        return (
            self.db.query(self.model)
            .filter(and_(self.model.user_id == user_id, self.model.date >= start_date))
            .order_by(desc(self.model.amount))
            .limit(limit)
            .all()
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _filtered_query(
        self,
        user_id: UUID,
        *,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        search: Optional[str] = None,
    ):
        query = self.db.query(self.model).filter(self.model.user_id == user_id)

        if start_date:
            query = query.filter(self.model.date >= start_date)
        if end_date:
            query = query.filter(self.model.date <= end_date)
        if category:
            query = query.filter(self.model.category == category)
        if min_amount is not None:
            query = query.filter(self.model.amount >= min_amount)
        if max_amount is not None:
            query = query.filter(self.model.amount <= max_amount)
        if search:
            pattern = f"%{search}%"
            query = query.filter(
                (self.model.description.ilike(pattern))
                | (self.model.merchant.ilike(pattern))
                | (self.model.subcategory.ilike(pattern))
            )

        return query

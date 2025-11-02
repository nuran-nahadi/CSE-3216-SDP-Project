from __future__ import annotations

from typing import Generic, Type, TypeVar

from sqlalchemy.orm import Session


ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Common helpers for repository implementations."""

    def __init__(self, db: Session, model: Type[ModelType]) -> None:
        self._db = db
        self._model = model

    @property
    def db(self) -> Session:
        return self._db

    @property
    def model(self) -> Type[ModelType]:
        return self._model

    def refresh(self, instance: ModelType) -> ModelType:
        self._db.refresh(instance)
        return instance

    def commit(self) -> None:
        self._db.commit()

    def rollback(self) -> None:
        self._db.rollback()

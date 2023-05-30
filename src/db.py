import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, Boolean, Date, Integer, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""


class Transaction(Base):
    """Model for a transaction."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tx_id: Mapped[int] = mapped_column(Integer)
    amount: Mapped[Decimal] = mapped_column(DECIMAL)
    date: Mapped[datetime.date] = mapped_column(Date)
    is_credit: Mapped[bool] = mapped_column(Boolean)
    file_id: Mapped[str] = mapped_column(Uuid)

import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, Boolean, Date, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[id] = mapped_column(Integer, primary_key=True)
    amount: Mapped[Decimal] = mapped_column(DECIMAL)
    date: Mapped[datetime.date] = mapped_column(Date)
    is_credit: Mapped[bool] = mapped_column(Boolean)

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Transaction:
    id: int
    date: datetime
    amount: Decimal
    is_credit: bool

    @classmethod
    def from_csv(cls, csv_line: str):
        id, date, amount = csv_line.split(",")
        is_credit = amount[0] == "+"
        return cls(
            id=int(id),
            date=datetime.strptime(date, "%m/%d"),
            amount=Decimal(amount[1:]),
            is_credit=is_credit,
        )
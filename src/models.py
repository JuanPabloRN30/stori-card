import datetime
from collections import namedtuple
from decimal import Decimal

GenerateReportCommand = namedtuple(
    "GenerateReportCommand", ["filepath", "receiver_email"]
)
ReportResult = namedtuple(
    "ReportResult",
    ["balance", "average_credit", "average_debit", "n_transactions_per_month"],
)


class Transaction(namedtuple("Transaction", ["id", "date", "amount", "is_credit"])):
    __slots__ = ()

    @classmethod
    def from_csv(cls, csv_line: str):
        id, date, amount = csv_line.split(",")
        is_credit = amount[0] == "+"
        return cls(
            id=int(id),
            date=datetime.datetime.strptime(date, "%m/%d"),
            amount=Decimal(amount[1:]),
            is_credit=is_credit,
        )

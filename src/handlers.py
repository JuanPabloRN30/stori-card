from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from commands.create_tx_file import Transaction


@dataclass
class ReportResult:
    total: Decimal
    average_credit: Decimal
    average_debit: Decimal
    n_transactions_per_month: list[int]


class ReportHandler(ABC):
    @abstractmethod
    def load(self, transaction: Transaction):
        pass

    @abstractmethod
    def calculate(self) -> ReportResult:
        pass


class InMemoryReportHandler(ReportHandler):
    N_TRANSACTIONS = 0
    SUM_CREDIT = 1
    SUM_DEBIT = 2

    def __init__(self):
        self.result = [[0 for _ in range(3)] for _ in range(12)]

    def load(self, transaction: Transaction):
        self.result[transaction.date.month - 1][self.N_TRANSACTIONS] += 1
        if transaction.is_credit:
            self.result[transaction.date.month - 1][
                self.SUM_CREDIT
            ] += transaction.amount
        else:
            self.result[transaction.date.month - 1][
                self.SUM_DEBIT
            ] += transaction.amount

    def calculate(self) -> ReportResult:
        n_transactions_per_month = []
        total_transactions = 0
        total_debit_amount = Decimal("0")
        total_credit_amount = Decimal("0")
        for month in self.result:
            month_transactions = month[self.N_TRANSACTIONS]
            n_transactions_per_month.append(month_transactions)

            total_transactions += month_transactions
            total_debit_amount += month[self.SUM_DEBIT]
            total_credit_amount += month[self.SUM_CREDIT]

        average_credit = self.__two_decimal_round(
            self.__safe_division(total_credit_amount, total_transactions)
        )
        average_debit = self.__two_decimal_round(
            self.__safe_division(total_debit_amount, total_transactions)
        )
        return ReportResult(
            total=total_credit_amount - total_debit_amount,
            average_credit=average_credit,
            average_debit=average_debit,
            n_transactions_per_month=n_transactions_per_month,
        )

    def __safe_division(self, a: Decimal, b: Decimal) -> Decimal:
        if b == 0:
            return Decimal("0")
        return a / b

    def __two_decimal_round(self, value: Decimal) -> Decimal:
        return Decimal(value).quantize(Decimal("0.01"))

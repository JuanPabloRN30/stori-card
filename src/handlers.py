from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import text

from commands.create_tx_file import Transaction
from db import Transaction as TransactionModel


# TODO: CHANGE IT TO NAMEDTUPLE
@dataclass
class ReportResult:
    balance: Decimal
    average_credit: Decimal
    average_debit: Decimal
    n_transactions_per_month: list[int]


class ReportHandler(ABC):
    """Abstract class to handle the report."""

    @abstractmethod
    def load(self, transaction: Transaction):
        """Load a transaction into the handler."""

    @abstractmethod
    def calculate(self) -> ReportResult:
        """Calculate the report."""

    def _safe_division(self, a: Decimal, b: Decimal) -> Decimal:
        """Safely divide two numbers."""
        if b == 0:
            return Decimal("0")
        return a / b

    def _two_decimal_round(self, value: Decimal) -> Decimal:
        """Round a number to two decimal places."""
        return Decimal(value).quantize(Decimal("0.01"))


class InMemoryReportHandler(ReportHandler):
    """In memory report handler."""

    N_TRANSACTIONS = 0
    SUM_CREDIT = 1
    SUM_DEBIT = 2

    def __init__(self):
        """Initialize the handler."""
        self.result = [[0 for _ in range(3)] for _ in range(12)]

    def load(self, transaction: Transaction):
        """Load a transaction into the handler."""
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
        """Calculate the report."""
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

        average_credit = self._two_decimal_round(
            self._safe_division(total_credit_amount, total_transactions)
        )
        average_debit = self._two_decimal_round(
            self._safe_division(total_debit_amount, total_transactions)
        )
        return ReportResult(
            balance=total_credit_amount - total_debit_amount,
            average_credit=average_credit,
            average_debit=average_debit,
            n_transactions_per_month=n_transactions_per_month,
        )


class SQLReportHandler(ReportHandler):
    """SQL report handler."""

    def __init__(self, session):
        """Initialize the handler."""
        self.session = session

    def load(self, transaction: Transaction):
        """Load a transaction into the handler."""
        self.session.add(
            TransactionModel(
                id=transaction.id,
                date=transaction.date,
                amount=transaction.amount,
                is_credit=transaction.is_credit,
            )
        )
        self.session.flush()

    def calculate(self) -> ReportResult:
        """Calculate the report."""

        calculate_query = """
        SELECT date_trunc('month', date) as month,
            count(*) as n_transactions,
            sum( CASE WHEN is_credit THEN amount ELSE 0 END ) as sum_credit,
            sum( CASE WHEN NOT is_credit THEN amount ELSE 0 END ) as sum_debit
        FROM transactions
        GROUP BY month
        """
        results = self.session.execute(text(calculate_query))

        n_transactions_per_month = [0] * 12
        total_transactions = 0
        total_credit_amount = Decimal("0")
        total_debit_amount = Decimal("0")
        for transaction_date, n_transactions, sum_credit, sum_debit in results:
            n_transactions_per_month[transaction_date.month - 1] = n_transactions
            total_transactions += n_transactions
            total_credit_amount += sum_credit
            total_debit_amount += sum_debit

        average_credit = self._two_decimal_round(
            self._safe_division(total_credit_amount, total_transactions)
        )
        average_debit = self._two_decimal_round(
            self._safe_division(total_debit_amount, total_transactions)
        )
        return ReportResult(
            balance=total_credit_amount - total_debit_amount,
            average_credit=average_credit,
            average_debit=average_debit,
            n_transactions_per_month=n_transactions_per_month,
        )

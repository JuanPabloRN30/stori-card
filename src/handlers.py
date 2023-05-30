import calendar
from abc import ABC, abstractmethod
from collections import defaultdict
from decimal import Decimal

from sqlalchemy import text

from commands.create_tx_file import Transaction
from db import Transaction as TransactionModel
from models import ReportInformationPerMonth, ReportResult


class ReportHandler(ABC):
    """Abstract class to handle the report."""

    @abstractmethod
    def load(self, transaction: Transaction, file_id: str):
        """Load a transaction into the handler."""

    @abstractmethod
    def calculate(self, file_id: str) -> ReportResult:
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

    def __init__(self):
        """Initialize the handler."""
        self.result = defaultdict(lambda: defaultdict(int))

    def load(self, transaction: Transaction, file_id: str):
        """Load a transaction into the handler."""

        month_name = calendar.month_name[transaction.date.month]

        if transaction.is_credit:
            self.result[month_name]["n_credit_transactions"] += 1
            self.result[month_name]["sum_credit"] += transaction.amount
        else:
            self.result[month_name]["n_debit_transactions"] += 1
            self.result[month_name]["sum_debit"] += transaction.amount

    def calculate(self, file_id: str) -> ReportResult:
        """Calculate the report."""
        information_per_month: list[ReportInformationPerMonth] = []
        total_credit_transactions = 0
        total_debit_transactions = 0
        total_debit_amount = Decimal("0")
        total_credit_amount = Decimal("0")
        for month, month_info in self.result.items():
            n_credit_transactions = month_info["n_credit_transactions"]
            n_debit_transactions = month_info["n_debit_transactions"]
            sum_credit = month_info["sum_credit"]
            sum_debit = month_info["sum_debit"]

            average_credit_per_month = self._two_decimal_round(
                self._safe_division(sum_credit, n_credit_transactions)
            )
            average_debit_per_month = self._two_decimal_round(
                self._safe_division(sum_debit, n_debit_transactions)
            )
            information_per_month.append(
                ReportInformationPerMonth(
                    month=month,
                    average_credit=average_credit_per_month,
                    average_debit=average_debit_per_month,
                    n_transactions=n_debit_transactions + n_credit_transactions,
                )
            )

            total_credit_transactions += n_credit_transactions
            total_debit_transactions += n_debit_transactions
            total_debit_amount += sum_debit
            total_credit_amount += sum_credit

        average_credit = self._two_decimal_round(
            self._safe_division(total_credit_amount, total_credit_transactions)
        )
        average_debit = self._two_decimal_round(
            self._safe_division(total_debit_amount, total_debit_transactions)
        )
        return ReportResult(
            balance=total_credit_amount - total_debit_amount,
            average_credit=average_credit,
            average_debit=average_debit,
            information_per_month=information_per_month,
        )


class SQLReportHandler(ReportHandler):
    """SQL report handler."""

    def __init__(self, session):
        """Initialize the handler."""
        self.session = session

    def load(self, transaction: Transaction, file_id: str):
        """Load a transaction into the handler."""
        self.session.add(
            TransactionModel(
                tx_id=transaction.id,
                date=transaction.date,
                amount=transaction.amount,
                is_credit=transaction.is_credit,
                file_id=file_id,
            )
        )
        self.session.flush()

    def calculate(self, file_id: str) -> ReportResult:
        """Calculate the report."""

        calculate_query = """
        SELECT date_trunc('month', date) as month,
            count( CASE WHEN is_credit THEN 1 ELSE NULL END ) as n_credit_transactions,
            count( CASE WHEN NOT is_credit THEN 1 ELSE NULL END ) as n_debit_transactions,
            sum( CASE WHEN is_credit THEN amount ELSE 0 END ) as sum_credit,
            sum( CASE WHEN NOT is_credit THEN amount ELSE 0 END ) as sum_debit
        FROM transactions
        WHERE file_id = :file_id
        GROUP BY month
        ORDER BY month;
        """  # noqa E501
        results = self.session.execute(text(calculate_query), {"file_id": file_id})

        information_per_month: list[ReportInformationPerMonth] = []
        total_credit_transactions = 0
        total_debit_transactions = 0
        total_credit_amount = Decimal("0")
        total_debit_amount = Decimal("0")
        for (
            transaction_date,
            n_credit_transactions,
            n_debit_transactions,
            sum_credit,
            sum_debit,
        ) in results:
            average_credit_per_month = self._two_decimal_round(
                self._safe_division(sum_credit, n_credit_transactions)
            )
            average_debit_per_month = self._two_decimal_round(
                self._safe_division(sum_debit, n_debit_transactions)
            )

            month_name = calendar.month_name[transaction_date.month]
            information_per_month.append(
                ReportInformationPerMonth(
                    month=month_name,
                    average_credit=average_credit_per_month,
                    average_debit=average_debit_per_month,
                    n_transactions=n_credit_transactions + n_debit_transactions,
                )
            )

            total_credit_transactions += n_credit_transactions
            total_debit_transactions += n_debit_transactions
            total_credit_amount += sum_credit
            total_debit_amount += sum_debit

        average_credit = self._two_decimal_round(
            self._safe_division(total_credit_amount, total_credit_transactions)
        )
        average_debit = self._two_decimal_round(
            self._safe_division(total_debit_amount, total_debit_transactions)
        )
        return ReportResult(
            balance=total_credit_amount - total_debit_amount,
            average_credit=average_credit,
            average_debit=average_debit,
            information_per_month=information_per_month,
        )

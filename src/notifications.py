import calendar
from abc import ABC, abstractmethod

from emails import Email
from handlers import ReportResult


class Notification(ABC):
    @abstractmethod
    def send(self, report_result: ReportResult, receivers: list[str]) -> None:
        pass


class EmailReportNotification(Notification):
    def __init__(self, email: Email) -> None:
        self.email: Email = email

    def send(self, report_result: ReportResult, receivers: list[str]) -> None:
        subject = "Transaction Report"
        body_data = [
            f"Total balance is {report_result.balance}",
            f"Average debit amount: {report_result.average_debit}",
            f"Average credit amount: {report_result.average_credit}",
        ]

        for month_number, transactions in enumerate(
            report_result.n_transactions_per_month
        ):
            if transactions == 0:
                continue

            month_name = calendar.month_name[month_number + 1]
            body_data.append(f"Number of transactions in {month_name}: {transactions}")

        body = "\n".join(body_data)
        self.email.send(subject, body, receivers)

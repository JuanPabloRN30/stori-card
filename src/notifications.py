import calendar
from abc import ABC, abstractmethod

from jinja2 import Environment, FileSystemLoader, select_autoescape

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
        body = self.__render_template(report_result)
        self.email.send(subject, body, receivers)

    def generate_email_body_kwargs(self, report_result: ReportResult) -> dict[str, str]:
        n_transactions_per_month = []
        for month_number, transactions in enumerate(
            report_result.n_transactions_per_month
        ):
            if transactions == 0:
                continue

            month_name = calendar.month_name[month_number + 1]
            n_transactions_per_month.append((month_name, transactions))
        return {
            "balance": report_result.balance,
            "average_debit": report_result.average_debit,
            "average_credit": report_result.average_credit,
            "n_transactions_per_month": n_transactions_per_month,
        }

    def __render_template(self, report_result: ReportResult) -> str:
        env = Environment(
            loader=FileSystemLoader(["./templates", "./src/templates"]),
            autoescape=select_autoescape(),
        )
        template = env.get_template("report.html")
        return template.render(**self.generate_email_body_kwargs(report_result))

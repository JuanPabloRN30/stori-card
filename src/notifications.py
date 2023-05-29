from abc import ABC, abstractmethod

from jinja2 import Environment, FileSystemLoader, select_autoescape

from emails import Email
from handlers import ReportResult


class Notification(ABC):
    """Abstract class to send notifications."""

    @abstractmethod
    def send(self, report_result: ReportResult, receivers: list[str]) -> None:
        """Send a report notification."""


class EmailReportNotification(Notification):
    """Class to send report notifications using email."""

    def __init__(self, email: Email) -> None:
        self.email: Email = email

    def send(self, report_result: ReportResult, receivers: list[str]) -> None:
        """Send a report notification."""
        subject = "Transaction Report"
        body = self.__render_template(report_result)
        self.email.send(subject, body, receivers)

    def __render_template(self, report_result: ReportResult) -> str:
        """Render the email template."""
        env = Environment(
            loader=FileSystemLoader(["./templates", "./src/templates"]),
            autoescape=select_autoescape(),
        )
        template = env.get_template("report.html")
        return template.render(**self.__generate_email_body_kwargs(report_result))

    def __generate_email_body_kwargs(
        self, report_result: ReportResult
    ) -> dict[str, str]:
        """Generate the keyword arguments for the email template."""
        information_per_month = {}
        for report_information_per_month in report_result.information_per_month:
            if report_information_per_month.n_transactions == 0:
                continue

            information_per_month[report_information_per_month.month] = {
                "average_credit": report_information_per_month.average_credit,
                "average_debit": report_information_per_month.average_debit,
                "n_transactions": report_information_per_month.n_transactions,
            }
        return {
            "balance": report_result.balance,
            "average_debit": report_result.average_debit,
            "average_credit": report_result.average_credit,
            "information_per_month": information_per_month,
        }

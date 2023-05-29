from emails import Email
from handlers import ReportResult
from notifications import EmailReportNotification


class FakeEmail(Email):
    def __init__(self, sender: str, password: str) -> None:
        self.sender = sender
        self.password = password
        self.subject = None
        self.body = None
        self.receivers = None

    def send(self, subject: str, body: str, receivers: list[str]) -> None:
        self.subject = subject
        self.body = body
        self.receivers = receivers


class TestEmailReportNotification:
    def test__send(self):
        # Arrange
        notification = EmailReportNotification(FakeEmail("", ""))
        report_result = ReportResult(
            balance=1000,
            average_debit=100,
            average_credit=200,
            n_transactions_per_month=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        )
        receivers = ["test@example.com"]

        # Act
        notification.send(report_result, receivers)

        # Assert
        assert notification.email.subject == "Transaction Report"
        assert notification.email.body is not None
        assert notification.email.receivers == ["test@example.com"]

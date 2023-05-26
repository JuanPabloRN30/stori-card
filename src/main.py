from emails import Email
from handlers import InMemoryReportHandler, ReportHandler
from models import Transaction
from notifications import EmailReportNotification, Notification


def read_transaction_file():
    with open("./tx_files/tx_file.csv", "r") as file:
        file.readline()  # skip header
        for line in file.readlines():
            yield line


def process_transaction_file(
    report_handler: ReportHandler, notification_service: Notification
) -> None:
    # Load transactions
    for line in read_transaction_file():
        transaction = Transaction.from_csv(line)
        report_handler.load(transaction)

    # Calculate report
    report_result = report_handler.calculate()

    # Send notification
    notification_service.send(report_result, ["test@example.com"])


if __name__ == "__main__":
    process_transaction_file(InMemoryReportHandler(), EmailReportNotification(Email))

from typing import Generator

from handlers import ReportHandler
from models import GenerateReportCommand, Transaction
from notifications import Notification


def read_transaction_file(filepath: str) -> Generator[str, None, None]:
    """Read a transaction file and yield each line."""
    with open(filepath, "r") as file:
        file.readline()  # skip header
        for line in file.readlines():
            yield line


def process_transaction_file(
    report_handler: ReportHandler,
    notification_service: Notification,
    command: GenerateReportCommand,
) -> None:
    """Process a transaction file and send a report notification."""
    # Load transactions
    for line in read_transaction_file(command.filepath):
        transaction = Transaction.from_csv(line)
        report_handler.load(transaction)

    # Calculate report
    report_result = report_handler.calculate()

    # Send notification
    notification_service.send(report_result, [command.receiver_email])

import click

from emails import Email
from handlers import InMemoryReportHandler
from models import GenerateReportCommand
from notifications import EmailReportNotification
from process import process_transaction_file


@click.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.argument("email", type=click.STRING)
def send_report(filepath: str, email: str) -> None:
    command = GenerateReportCommand(filepath=filepath, receiver_email=email)
    process_transaction_file(
        InMemoryReportHandler(), EmailReportNotification(Email), command
    )


if __name__ == "__main__":
    send_report()

import click

from boostrap import get_session
from constants import DATABASE_URL, EMAIL_PASSWORD, EMAIL_SENDER
from emails import Email
from handlers import InMemoryReportHandler, SQLReportHandler
from models import GenerateReportCommand
from notifications import EmailReportNotification
from process import process_transaction_file


@click.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.argument("email", type=click.STRING)
def send_report(filepath: str, email: str) -> None:
    """Command to process a transaction file and send the report by email."""
    command = GenerateReportCommand(filepath=filepath, receiver_email=email)
    email = Email(EMAIL_SENDER, EMAIL_PASSWORD)

    if DATABASE_URL:
        session = get_session()
        process_transaction_file(
            SQLReportHandler(session), EmailReportNotification(email), command
        )
        session.commit()
        session.close()
    else:
        process_transaction_file(
            InMemoryReportHandler(), EmailReportNotification(email), command
        )

    click.echo("Report sent!")


if __name__ == "__main__":
    send_report()

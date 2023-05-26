import datetime
import random

import click

from models import Transaction

UPPER_LIMIT = 10000


@click.command()
@click.option("--location", help="Destination folder of the file.")
@click.option("--filename", help="Name of the file.")
@click.option("--n_credit", default=1, help="Number of credit transactions.")
@click.option("--n_debit", default=1, help="Number of debit transactions.")
def create_tx_file(location: str, filename: str, n_credit: int, n_debit: int) -> None:
    """Generate a CSV file with random transactions."""
    validate_upper_limit(n_credit)
    validate_upper_limit(n_debit)

    if not location:
        location = "./tx_files"

    if not filename:
        filename = "tx_file.csv"

    transactions = generate_transactions(n_credit, n_debit)
    file_path = f"{location}/{filename}"

    with open(file_path, "w") as f:
        f.write("Id,Date,Transaction\n")
        for transaction in transactions:
            transaction_date = transaction.date.strftime("%m/%d")
            sign = "+" if transaction.is_credit else "-"
            f.write(f"{transaction.id},{transaction_date},{sign}{transaction.amount}\n")
    click.echo(f"File {file_path} generated!")


def validate_upper_limit(value: int) -> None:
    if value >= UPPER_LIMIT:
        raise click.BadParameter(f"Value must be less than {UPPER_LIMIT}")


def generate_transactions(n_credit: int, n_debit: int) -> list[Transaction]:
    START_DATE = datetime.datetime(2023, 1, 1)
    END_DATE = datetime.datetime(2023, 12, 31)
    transactions: list[Transaction] = []

    for i in range(n_credit):
        random_date = calculate_random_date(START_DATE, END_DATE)
        random_amount = calculate_random_amount()
        transactions.append(Transaction(i, random_date, random_amount, True))

    for i in range(n_credit, n_credit + n_debit):
        random_date = calculate_random_date(START_DATE, END_DATE)
        random_amount = calculate_random_amount()
        transactions.append(Transaction(i, random_date, random_amount, False))

    transactions.sort(key=lambda x: x.date)
    return transactions


def calculate_random_date(
    start_date: datetime.datetime, end_date: datetime.datetime
) -> datetime.datetime:
    return start_date + datetime.timedelta(
        seconds=random.randint(0, int((end_date - start_date).total_seconds())),
    )


def calculate_random_amount(low: int = 1, high: int = 200) -> int:
    return random.randint(low, high)


if __name__ == "__main__":
    create_tx_file()

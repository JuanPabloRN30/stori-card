from handlers import InMemoryReportHandler, ReportHandler
from models import Transaction


def read_transaction_file():
    with open("./tx_files/tx_file.csv", "r") as file:
        file.readline()  # skip header
        for line in file.readlines():
            yield line


def process_transaction_file(report_handler: ReportHandler) -> None:
    for line in read_transaction_file():
        transaction = Transaction.from_csv(line)
        report_handler.load(transaction)

    report_result = report_handler.calculate()
    print(report_result)


if __name__ == "__main__":
    process_transaction_file(InMemoryReportHandler())

import uuid
from datetime import datetime
from decimal import Decimal

from commands.create_tx_file import Transaction
from db import Transaction as TransactionModel
from handlers import InMemoryReportHandler, SQLReportHandler
from models import ReportInformationPerMonth


def create_transaction(**kwargs) -> Transaction:
    default_kwargs = {
        "id": 0,
        "date": convert_str_to_date("01/01"),
        "amount": Decimal("10"),
        "is_credit": True,
    }
    default_kwargs.update(kwargs)
    return Transaction(**default_kwargs)


def convert_str_to_date(date: str) -> datetime:
    return datetime.strptime(date, "%m/%d")


def retrieve_file_id() -> uuid.UUID:
    return uuid.uuid4()


class TestInMemoryHandler:
    def test__load__should_increase_credit_transactions(self):
        # Arrange
        handler = InMemoryReportHandler()
        transaction = create_transaction()

        # Act
        handler.load(transaction, retrieve_file_id())

        # Assert
        assert handler.result["January"]["n_credit_transactions"] == 1

    def test__load__should_increase_debit_transactions(self):
        # Arrange
        handler = InMemoryReportHandler()
        transaction = create_transaction(is_credit=False)

        # Act
        handler.load(transaction, retrieve_file_id())

        # Assert
        assert handler.result["January"]["n_debit_transactions"] == 1

    def test__load__should_increase_sum_credit(self):
        # Arrange
        handler = InMemoryReportHandler()
        transaction = create_transaction()

        # Act
        handler.load(transaction, retrieve_file_id())

        # Assert
        assert handler.result["January"]["sum_credit"] == 10
        assert handler.result["January"]["sum_debit"] == 0

    def test__load__should_increase_sum_debit(self):
        # Arrange
        handler = InMemoryReportHandler()
        transaction = create_transaction(is_credit=False)

        # Act
        handler.load(transaction, retrieve_file_id())

        # Assert
        assert handler.result["January"]["sum_debit"] == 10
        assert handler.result["January"]["sum_credit"] == 0

    def test__calculate__should_return_total(self):
        # Arrange
        handler = InMemoryReportHandler()
        transaction = create_transaction()
        file_id = retrieve_file_id()
        handler.load(transaction, file_id)

        # Act
        result = handler.calculate(file_id)

        # Assert
        assert result.balance == Decimal("10")

    def test__calculate__should_return_average_credit(self):
        # Arrange
        handler = InMemoryReportHandler()
        transaction = create_transaction()
        file_id = retrieve_file_id()
        handler.load(transaction, file_id)
        transaction = create_transaction(amount=Decimal("20"))
        handler.load(transaction, file_id)

        # Act
        result = handler.calculate(file_id)

        # Assert
        assert result.average_credit == Decimal("15")

    def test__calculate__should_return_average_debit(self):
        # Arrange
        handler = InMemoryReportHandler()
        transaction = create_transaction(is_credit=False, amount=Decimal("20"))
        file_id = retrieve_file_id()
        handler.load(transaction, file_id)
        transaction = create_transaction(is_credit=False, amount=Decimal("100"))
        handler.load(transaction, file_id)

        # Act
        result = handler.calculate(file_id)

        # Assert
        assert result.average_debit == Decimal("60")

    def test__calculate__should_return_information_per_month(self):
        # Arrange
        handler = InMemoryReportHandler()
        transaction = create_transaction()
        file_id = retrieve_file_id()
        handler.load(transaction, file_id)

        transaction = create_transaction(date=convert_str_to_date("12/01"))
        handler.load(transaction, file_id)

        # Act
        result = handler.calculate(file_id)

        # Assert
        expected_result = [
            ReportInformationPerMonth(
                month="January",
                average_credit=Decimal("10"),
                average_debit=Decimal("0"),
                n_transactions=1,
            ),
            ReportInformationPerMonth(
                month="December",
                average_credit=Decimal("10"),
                average_debit=Decimal("0"),
                n_transactions=1,
            ),
        ]
        assert result.information_per_month == expected_result

    def test__safe_division__should_return_zero(self):
        # Arrange
        handler = InMemoryReportHandler()
        file_id = retrieve_file_id()

        # Act
        result = handler.calculate(file_id)

        # Assert
        assert result.average_credit == Decimal("0")


class TestSQLReportHandler:
    def test__load__store_transaction(self, session):
        # Arrange
        handler = SQLReportHandler(session)
        transaction = create_transaction()

        # Act
        handler.load(transaction, retrieve_file_id())

        # Assert
        assert session.query(TransactionModel).count() == 1

    def test__calculate__should_return_total(self, session):
        # Arrange
        handler = SQLReportHandler(session)
        transaction = create_transaction()
        file_id = retrieve_file_id()
        handler.load(transaction, file_id)

        # Act
        result = handler.calculate(file_id)

        # Assert
        assert result.balance == Decimal("10")

    def test__calculate__should_return_average_credit(self, session):
        # Arrange
        handler = SQLReportHandler(session)
        transaction = create_transaction()
        file_id = retrieve_file_id()
        handler.load(transaction, file_id)
        transaction = create_transaction(id=1, amount=Decimal("20"))
        handler.load(transaction, file_id)

        # Act
        result = handler.calculate(file_id)

        # Assert
        assert result.average_credit == Decimal("15")

    def test__calculate__should_return_average_debit(self, session):
        # Arrange
        handler = SQLReportHandler(session)
        file_id = retrieve_file_id()
        transaction = create_transaction(is_credit=False, amount=Decimal("20"))
        handler.load(transaction, file_id)
        transaction = create_transaction(id=1, is_credit=False, amount=Decimal("100"))
        handler.load(transaction, file_id)

        # Act
        result = handler.calculate(file_id)

        # Assert
        assert result.average_debit == Decimal("60")

    def test__calculate__should_return_n_transactions_per_month(self, session):
        # Arrange
        handler = SQLReportHandler(session)
        file_id = retrieve_file_id()
        transaction = create_transaction()
        handler.load(transaction, file_id)

        transaction = create_transaction(id=1, date=convert_str_to_date("12/01"))
        handler.load(transaction, file_id)

        # Act
        result = handler.calculate(file_id)

        # Assert
        expected_result = [
            ReportInformationPerMonth(
                month="January",
                average_credit=Decimal("10"),
                average_debit=Decimal("0"),
                n_transactions=1,
            ),
            ReportInformationPerMonth(
                month="December",
                average_credit=Decimal("10"),
                average_debit=Decimal("0"),
                n_transactions=1,
            ),
        ]
        assert result.information_per_month == expected_result

    def test__safe_division__should_return_zero(self, session):
        # Arrange
        handler = SQLReportHandler(session)
        file_id = retrieve_file_id()

        # Act
        result = handler.calculate(file_id)

        # Assert
        assert result.average_credit == Decimal("0")

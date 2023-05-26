from datetime import datetime
from decimal import Decimal

from commands.create_tx_file import Transaction
from handlers import InMemoryReportHandler


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


class TestInMemoryHandler:
    def test__load__should_increase_n_transactions(self):
        # Arrange
        handler = InMemoryReportHandler()
        transaction = create_transaction()

        # Act
        handler.load(transaction)

        # Assert
        assert handler.result[0][0] == 1

    def test__load__should_increase_sum_credit(self):
        # Arrange
        handler = InMemoryReportHandler()
        transaction = create_transaction()

        # Act
        handler.load(transaction)

        # Assert
        assert handler.result[0][1] == 10
        assert handler.result[0][2] == 0

    def test__load__should_increase_sum_debit(self):
        # Arrange
        handler = InMemoryReportHandler()
        transaction = create_transaction(is_credit=False)

        # Act
        handler.load(transaction)

        # Assert
        assert handler.result[0][2] == 10
        assert handler.result[0][1] == 0

    def test__calculate__should_return_total(self):
        # Arrange
        handler = InMemoryReportHandler()
        transaction = create_transaction()
        handler.load(transaction)

        # Act
        result = handler.calculate()

        # Assert
        assert result.balance == Decimal("10")

    def test__calculate__should_return_average_credit(self):
        # Arrange
        handler = InMemoryReportHandler()
        transaction = create_transaction()
        handler.load(transaction)
        transaction = create_transaction(amount=Decimal("20"))
        handler.load(transaction)

        # Act
        result = handler.calculate()

        # Assert
        assert result.average_credit == Decimal("15")

    def test__calculate__should_return_average_debit(self):
        # Arrange
        handler = InMemoryReportHandler()
        transaction = create_transaction(is_credit=False, amount=Decimal("20"))
        handler.load(transaction)
        transaction = create_transaction(is_credit=False, amount=Decimal("100"))
        handler.load(transaction)

        # Act
        result = handler.calculate()

        # Assert
        assert result.average_debit == Decimal("60")

    def test__calculate__should_return_n_transactions_per_month(self):
        # Arrange
        handler = InMemoryReportHandler()
        transaction = create_transaction()
        handler.load(transaction)

        transaction = create_transaction(date=convert_str_to_date("12/01"))
        handler.load(transaction)

        # Act
        result = handler.calculate()

        # Assert
        expected_result = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        assert result.n_transactions_per_month == expected_result

    def test__safe_division__should_return_zero(self):
        # Arrange
        handler = InMemoryReportHandler()

        # Act
        result = handler.calculate()

        # Assert
        assert result.average_credit == Decimal("0")

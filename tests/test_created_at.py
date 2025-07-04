import datetime
import uuid
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import Base, Transaction


class TestCreatedAtTimestamp:
    """Test that the created_at timestamp is properly set on base model."""

    def setup_method(self):
        """Set up an in-memory database for each test."""
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self):
        """Clean up after each test."""
        self.session.close()

    def test_transaction_gets_created_at_timestamp(self):
        """Test that a new Transaction record gets a created_at timestamp."""
        # Arrange
        transaction = Transaction(
            tx_id=1,
            amount=Decimal("100.50"),
            date=datetime.date(2023, 1, 15),
            is_credit=True,
            file_id=uuid.uuid4(),
        )

        # Act
        self.session.add(transaction)
        self.session.commit()

        # Assert
        result = self.session.query(Transaction).first()
        assert result.created_at is not None
        assert isinstance(result.created_at, datetime.datetime)

    def test_multiple_transactions_get_different_timestamps(self):
        """Test that multiple transactions can have different created_at timestamps."""
        # Arrange
        transaction1 = Transaction(
            tx_id=1,
            amount=Decimal("100.00"),
            date=datetime.date(2023, 1, 15),
            is_credit=True,
            file_id=uuid.uuid4(),
        )
        transaction2 = Transaction(
            tx_id=2,
            amount=Decimal("200.00"),
            date=datetime.date(2023, 1, 16),
            is_credit=False,
            file_id=uuid.uuid4(),
        )

        # Act
        self.session.add(transaction1)
        self.session.commit()

        self.session.add(transaction2)
        self.session.commit()

        # Assert
        results = self.session.query(Transaction).order_by(Transaction.id).all()
        assert len(results) == 2
        assert results[0].created_at is not None
        assert results[1].created_at is not None
        # Second transaction timestamp should not be earlier than first
        assert results[1].created_at >= results[0].created_at

    def test_created_at_is_immutable_after_creation(self):
        """Test that created_at timestamp doesn't change when record is updated."""
        # Arrange
        transaction = Transaction(
            tx_id=1,
            amount=Decimal("100.00"),
            date=datetime.date(2023, 1, 15),
            is_credit=True,
            file_id=uuid.uuid4(),
        )
        self.session.add(transaction)
        self.session.commit()

        # Get the original created_at timestamp
        original_created_at = transaction.created_at

        # Act - update the transaction
        transaction.amount = Decimal("200.00")
        self.session.commit()

        # Assert - created_at should remain the same
        self.session.refresh(transaction)
        assert transaction.created_at == original_created_at

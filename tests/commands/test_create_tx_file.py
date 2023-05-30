import os

from click.testing import CliRunner

from commands.create_tx_file import create_tx_file


def test_create_tx_file():
    # Arrange
    runner = CliRunner()

    # Act
    result = runner.invoke(
        create_tx_file,
        [
            "--filename",
            "test.csv",
            "--n_credit",
            2,
            "--n_debit",
            2,
        ],
    )

    # Assert
    assert result.exit_code == 0
    assert result.output == "File ./tx_files/test.csv generated!\n"
    assert os.path.exists("./tx_files/test.csv")

    # Cleanup
    os.remove("./tx_files/test.csv")

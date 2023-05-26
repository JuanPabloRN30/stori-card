import os
from click.testing import CliRunner

from commands.create_tx_file import create_tx_file


def test_create_tx_file(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        result = runner.invoke(
            create_tx_file,
            [
                "--location",
                tmp_path,
                "--filename",
                "test.csv",
                "--n_credit",
                2,
                "--n_debit",
                2,
            ],
        )
    assert result.exit_code == 0
    assert result.output == f"File {tmp_path}/test.csv generated!\n"
    assert os.path.exists(f"{tmp_path}/test.csv")

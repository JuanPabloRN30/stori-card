# stori-card

## Commands

### Create Transaction File

The project has a command to create a transaction file with random data. To run this command put the following line in your terminal

```bash
poetry run python src/commands/create_tx_file.py
```

By default, the file is created with just two lines (one debit and one credit) to add more lines you can use optional arguments. In the following example, the file will have 100 credit transactions and 100 debit transactions

```bash
poetry run python src/commands/create_tx_file.py --n_credit 100 --n_debit 100
```

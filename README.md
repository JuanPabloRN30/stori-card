# stori-card

## Pre-Requisites

To send the report via email you need to configure first the `EMAIL_SENDER` and `EMAIL_PASSWORD` environment variables. Those variables are needed to login in the email service.

> The email service used is Gmail.

## How To Run

There are two ways to run this project.
1. Docker
2. Locally

### 1. Docker

To run using it Docker, follow the step-by-step

1.1 Build the Docker image

```bash
docker compose build
```

1.2 Send the report. Don't forget to put the transaction file path and the receiver email

```bash
docker compose run --rm report poetry run python ./commands/send_report.py <path/to/transactions.csv> <test@example.com>
```

1.3 After that, you can check the email to read the generated report

### 2. Locally

1.1 To run locally, first we need to install `poetry`. To do that you can follow the installation instructions [here](https://python-poetry.org/docs/#installation)

1.2 Install the dependencies

```bash
poetry install
```

1.3 You're ready to go. To send the report put the following command in your terminal

```bash
poetry run python src/commands/create_tx_file.py <path/to/report.csv> <test@example.com>
```

1.4 After that, you can check the email to read the generated report

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

### Send Report Email

The project has a command to send the report created by using the transaction file. To run this command put the following line in your terminal, don't forget to update the path to the file and the email of the person who is going to receive the report

```bash
poetry run python src/commands/create_tx_file.py <path/to/report.csv> <test@example.com>
```

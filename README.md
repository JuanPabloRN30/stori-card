# stori-card

## Pre-Requisites

To send the report via email you need to configure first the `EMAIL_SENDER` and `EMAIL_PASSWORD` environment variables. Those variables are needed to login in the email service.

> The email service used is Gmail and you can generate the password following these instructions [doc](https://support.google.com/accounts/answer/185833?hl=en)

## How To Run

### Docker

To run using it Docker, follow the step-by-step

1. Build the Docker image

```bash
docker compose build
```

2. Run migrations in the database

```bash
docker compose run --rm report alembic upgrade head
```

3. Send the report. Don't forget to put the transaction file path and the receiver email

```bash
docker compose run --rm report python ./commands/send_report.py ./tx_files/tx_file.csv example@example.com
```

> If you want to generate a new file you can execute this [command](https://github.com/JuanPabloRN30/stori-card#create-transaction-file)

4. After that, you can check the email to read the generated report

## Commands

### Create Transaction File

The project has a command to create a transaction file with random data. To run this command put the following line in your terminal

```bash
docker compose run --rm report python ./commands/create_tx_file.py
```

By default, the file created is `./tx_files/tx_file.csv` with just two lines (one debit and one credit) to change the `filename` or to `add more lines` you can use optional arguments. In the following example, the file will have 100 credit transactions and 100 debit transactions

```bash
docker compose run --rm report python ./commands/create_tx_file.py --filename new_tx_file.csv --n_credit 100 --n_debit 100
```

### Send Report Email

The project has a command to send the report created by using the transaction file. To run this command put the following line in your terminal, don't forget to update the path to the file and the email of the person who is going to receive the report

```bash
docker compose run --rm report python src/commands/create_tx_file.py <path/to/report.csv> <test@example.com>
```

## Cloud

To deploy it to the cloud there's a solution in AWS. The main idea is when you put a file in S3 a Lambda will be triggered and it will send the report via email.

To create this solution in AWS you should enter into the `tf` folder and run `terraform plan` and `terraform apply` commands.

After that, you need to push the Lambda Docker image, to do that in the `Makefile` you will find a couple of commands.

```bash
make lambda/push
```

Finally, put a file inside the bucket and the lambda will process it and it will send the report

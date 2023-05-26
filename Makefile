linter:
	poetry run ruff .

formatter:
	poetry run black . && poetry run isort .

test:
	PYTHONPATH=./src poetry run pytest

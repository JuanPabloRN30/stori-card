linter:
	poetry run ruff .

formatter:
	poetry run black . && poetry run isort .

test:
	docker compose up database -d
	PYTHONPATH=./src poetry run pytest
	docker compose stop database

lambda/build:
	docker buildx build --platform linux/amd64 -t lambda-build -f Dockerfile.lambda .

lambda/push: lambda/build
	aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
	docker tag lambda-build:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/stori-card-processor:latest
	docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/stori-card-processor:latest

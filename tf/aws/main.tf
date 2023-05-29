resource "aws_s3_bucket" "assets" {
  bucket = "stori-card-assets"
}

resource "aws_s3_bucket_public_access_block" "assets_public_access" {
  bucket = aws_s3_bucket.assets.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_ownership_controls" "assets_ownership" {
  bucket = aws_s3_bucket.assets.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "assets_acl" {
  depends_on = [
    aws_s3_bucket_ownership_controls.assets_ownership,
    aws_s3_bucket_public_access_block.assets_public_access,
  ]

  bucket = aws_s3_bucket.assets.id
  acl    = "public-read"
}

resource "aws_s3_bucket_policy" "prod_website" {
  bucket = aws_s3_bucket.assets.id
  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
      {
          "Sid": "PublicReadGetObject",
          "Effect": "Allow",
          "Principal": "*",
          "Action": [
             "s3:GetObject"
          ],
          "Resource": [
             "arn:aws:s3:::${aws_s3_bucket.assets.id}/*"
          ]
      }
    ]
}
POLICY
}


resource "aws_s3_bucket" "transactions-bucket" {
  bucket = "stori-card-transactions"
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "aws_iam_policy" "cloudwatch_managed_policy" {
  arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "sto-readonly-role-policy-attach" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = data.aws_iam_policy.cloudwatch_managed_policy.arn
}

resource "aws_iam_policy" "custom_policy" {
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ssm:GetParameter",
        ]
        Effect   = "Allow"
        Resource = aws_ssm_parameter.email_sender.arn
      },
      {
        Action = [
          "ssm:GetParameter",
        ]
        Effect   = "Allow"
        Resource = aws_ssm_parameter.email_password.arn
      },
      {
        Action = [
          "s3:GetObject",
        ]
        Effect   = "Allow"
        Resource = "arn:aws:s3:::stori-card-transactions/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "custom-policy-attach" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.custom_policy.arn
}

resource "aws_lambda_function" "processor-lambda" {
  function_name = "stori-card-lambda-processor"
  image_uri     = "${aws_ecr_repository.stori_card_processor.repository_url}:latest"
  package_type  = "Image"

  role = aws_iam_role.iam_for_lambda.arn
  timeout = 10

  environment {
    variables = {
      EMAIL_RECEIVER = var.email_receiver
      EMAIL_SENDER   = aws_ssm_parameter.email_sender.name
      EMAIL_PASSWORD = aws_ssm_parameter.email_password.name
    }
  }
}

resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.processor-lambda.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.transactions-bucket.arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.transactions-bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.processor-lambda.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_bucket]
}

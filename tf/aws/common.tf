resource "aws_ecr_repository" "stori_card_processor" {
  name = "stori-card-processor"
}

resource "aws_ssm_parameter" "email_sender" {
  name  = "email_sender"
  type  = "String"
  value = var.email_sender
}

resource "aws_ssm_parameter" "email_password" {
  name  = "email_password"
  type  = "String"
  value = var.email_password
}

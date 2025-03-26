resource "aws_dynamodb_table" "terraform_lock" {
  name           = "${var.github_acc}-${var.aws_region}-terraform-lock"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
  tags = local.common_tags
}
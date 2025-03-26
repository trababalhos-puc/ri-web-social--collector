resource "aws_s3_bucket" "s3_buckets" {
  bucket = lower("${var.aws_region}-${var.github_acc}--tfstates")
  tags = local.common_tags
}

resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
  tags = local.common_tags
  client_id_list = [
    "sts.amazonaws.com",
  ]

  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
  ]
}

resource "aws_iam_role" "github_actions_role" {
  name = "github-actions-role-${var.github_acc}-${var.aws_region}"
  tags = local.common_tags
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        },
        Action = "sts:AssumeRoleWithWebIdentity",
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" : ["sts.amazonaws.com"]
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" : ["repo:${var.github_acc}/*"]
          }
        }
      }
    ]
  })
}

resource "aws_iam_policy" "github_actions_policy_dynamodb" {
  name        = "github-actions-policy-dynamodb-${var.github_acc}-${var.aws_region}"
  description = "Politica para permitir que GitHub Actions interaja com recursos no AWS"
  tags = local.common_tags
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:DeleteItem"
        ],
        Resource = aws_dynamodb_table.terraform_lock.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_policy_dynamo" {
  role       = aws_iam_role.github_actions_role.name
  policy_arn = aws_iam_policy.github_actions_policy_dynamodb.arn
}
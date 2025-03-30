resource "aws_iam_policy" "github_actions_policy" {
  name        = "github-actions-policy-${var.github_acc}-${var.aws_region}"
  description = "Politica para permitir que GitHub Actions interaja com recursos no AWS"
  tags = local.common_tags
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "s3:*",
          "ecs:*",
          "ecr:*",
          "iam:CreatePolicy",
          "iam:CreateRole",
          "events:*",
          "logs:*",
          "elasticloadbalancing:*"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_policy" {
  role       = aws_iam_role.github_actions_role.name
  policy_arn = aws_iam_policy.github_actions_policy.arn
}
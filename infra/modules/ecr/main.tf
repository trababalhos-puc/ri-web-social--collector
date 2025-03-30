# -*- coding: utf-8 -*-
# File name infra/modules/ecr/main.tf

data "aws_caller_identity" "current" {}

locals {
  aws_account_id = data.aws_caller_identity.current.account_id

  raw_name = lower("${var.TagEnv}-${var.repository_name}")

  clean_name_step1 = replace(local.raw_name, "/[^a-z0-9._-]/", "")

  clean_name_step2 = replace(
    replace(
      replace(local.clean_name_step1, "--+", "-"),
      "\\.\\.+", "."
    ),
    "__+", "_"
  )

  clean_name_step3 = replace(
    replace(local.clean_name_step2, "/^-+/", ""),
    "/-+$/", ""
  )
  repository_name = length(local.clean_name_step3) > 0 ? local.clean_name_step3 : "default-repo"
}

resource "aws_ecr_repository" "this" {
  name                 = local.repository_name
  image_tag_mutability = var.image_tag_mutability
  image_scanning_configuration {
    scan_on_push = var.scan_on_push
  }
  tags = var.tags
}


resource "aws_ecr_lifecycle_policy" "delete" {
  repository = aws_ecr_repository.this.name
  policy     = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Keep only the most recent images",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": ${var.days_lifecycle_policy}
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}
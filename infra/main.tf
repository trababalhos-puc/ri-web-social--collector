# Atualização do módulo VPC no arquivo principal (main.tf)

module "vpc" {
  source            = "./modules/vpc"
  TagEnv            = var.TagEnv
  TagProject        = var.TagProject
  name_prefix       = "ecs"
  region            = var.aws_region
  az_count          = 2
  nat_gateway_count = 1
  tags              = local.common_tags
}

module "bucket" {
  source       = "./modules/s3"
  TagEnv       = var.TagEnv
  TagProject   = var.TagProject
  bucket_names = ["trab"]
  region       = var.aws_region
  tags         = local.common_tags
}

module "ecr" {
  source          = "./modules/ecr"
  TagEnv          = var.TagEnv
  TagProject      = var.TagProject
  region          = var.aws_region
  repository_name = "collector"
  tags            = local.common_tags
  folder          = "src"
}

resource "aws_iam_policy" "ecs_policy" {
  name        = "${var.TagEnv}-${var.TagProject}-ecs-access"
  description = "Permite acesso completo ao S3 para as tarefas ECS"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:*",
          "logs:*",
          "ecr:*"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

module "ecs" {
  source             = "./modules/ecs"
  TagEnv             = var.TagEnv
  TagProject         = var.TagProject
  region             = var.aws_region
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids
  ecr_repository_url = module.ecr.repository_url
  iam_policy_arns = [
    aws_iam_policy.ecs_policy.arn
  ]
  task_cpu              = 256
  task_memory           = 512
  service_desired_count = 1
  assign_public_ip      = false
  container_port        = 8080
  health_check_path     = "/"
  enable_https          = false
  tags                  = local.common_tags
}
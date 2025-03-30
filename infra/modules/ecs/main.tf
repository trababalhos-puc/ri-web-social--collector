resource "aws_ecs_cluster" "app_cluster" {
  name = "${var.TagEnv}-${var.TagProject}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = var.tags
}

resource "aws_ecs_task_definition" "app_task" {
  family                   = "${var.TagEnv}-${var.TagProject}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "${var.TagEnv}-${var.TagProject}-container"
      image     = "${var.ecr_repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.app_logs.name
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      environment = var.container_environment
    }
  ])

  tags = var.tags
}

# Comentado o recurso de serviço ECS contínuo
# resource "aws_ecs_service" "app_service" {
#   name                               = "${var.TagEnv}-${var.TagProject}-service"
#   cluster                            = aws_ecs_cluster.app_cluster.id
#   task_definition                    = aws_ecs_task_definition.app_task.arn
#   desired_count                      = var.service_desired_count
#   deployment_minimum_healthy_percent = 100
#   deployment_maximum_percent         = 200
#   launch_type                        = "FARGATE"
#   scheduling_strategy                = "REPLICA"

#   network_configuration {
#     security_groups  = [aws_security_group.ecs_service_sg.id]
#     subnets          = var.subnet_ids
#     assign_public_ip = var.assign_public_ip
#   }

#   load_balancer {
#     target_group_arn = aws_lb_target_group.app_tg.arn
#     container_name   = "${var.TagEnv}-${var.TagProject}-container"
#     container_port   = var.container_port
#   }

#   lifecycle {
#     ignore_changes = [task_definition, desired_count]
#   }

#   depends_on = [aws_lb_listener.app_listener]

#   tags = var.tags
# }

# EventBridge (CloudWatch Events) rule para programar a execução da tarefa
resource "aws_cloudwatch_event_rule" "scheduled_task" {
  name                = "${var.TagEnv}-${var.TagProject}-schedule-rule"
  description         = "Regra para execução programada da tarefa ${var.TagEnv}-${var.TagProject}"
  schedule_expression = var.schedule_expression

  tags = var.tags
}

# Target para o EventBridge que executa a tarefa ECS
resource "aws_cloudwatch_event_target" "ecs_scheduled_task" {
  rule      = aws_cloudwatch_event_rule.scheduled_task.name
  target_id = "${var.TagEnv}-${var.TagProject}-target"
  arn       = aws_ecs_cluster.app_cluster.arn
  role_arn  = aws_iam_role.events_role.arn

  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.app_task.arn
    launch_type         = "FARGATE"
    platform_version    = "LATEST"

    network_configuration {
      subnets          = var.subnet_ids
      security_groups  = [aws_security_group.ecs_service_sg.id]
      assign_public_ip = var.assign_public_ip
    }
  }
}

# IAM Role para o EventBridge executar tarefas no ECS
resource "aws_iam_role" "events_role" {
  name = "${var.TagEnv}-${var.TagProject}-events-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# IAM Policy para permitir que o EventBridge execute tarefas no ECS
resource "aws_iam_policy" "events_policy" {
  name        = "${var.TagEnv}-${var.TagProject}-events-policy"
  description = "Permite que o EventBridge execute tarefas no ECS"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ecs:RunTask"
        Resource = aws_ecs_task_definition.app_task.arn
        Condition = {
          ArnEquals = {
            "ecs:cluster" = aws_ecs_cluster.app_cluster.arn
          }
        }
      },
      {
        Effect = "Allow"
        Action = "iam:PassRole"
        Resource = [
          aws_iam_role.ecs_task_role.arn,
          aws_iam_role.ecs_execution_role.arn
        ]
      }
    ]
  })
}

# Anexar a política IAM ao role do EventBridge
resource "aws_iam_role_policy_attachment" "events_role_policy" {
  role       = aws_iam_role.events_role.name
  policy_arn = aws_iam_policy.events_policy.arn
}

resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/ecs/${var.TagEnv}-${var.TagProject}"
  retention_in_days = 30

  tags = var.tags
}

# IAM Roles para o ECS
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.TagEnv}-${var.TagProject}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task_role" {
  name = "${var.TagEnv}-${var.TagProject}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# Anexa políticas IAM adicionais ao task role do ECS
resource "aws_iam_role_policy_attachment" "ecs_task_role_policy_attachments" {
  count      = length(var.iam_policy_arns)
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = var.iam_policy_arns[count.index]
}

# Security Group para o ECS Service
resource "aws_security_group" "ecs_service_sg" {
  name        = "${var.TagEnv}-${var.TagProject}-ecs-service-sg"
  description = "Security group for the ECS service"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = var.container_port
    to_port     = var.container_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

# Application Load Balancer - você pode decidir se quer manter ou comentar
# dependendo se precisa de acesso externo ao container
# resource "aws_lb" "app_lb" {
#   name               = "${var.TagEnv}-${var.TagProject}-alb"
#   internal           = false
#   load_balancer_type = "application"
#   security_groups    = [aws_security_group.alb_sg.id]
#   subnets            = var.subnet_ids
#
#   enable_deletion_protection = false
#
#   tags = var.tags
# }

resource "aws_security_group" "alb_sg" {
  name        = "${var.TagEnv}-${var.TagProject}-alb-sg"
  description = "Security group for the application load balancer"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

resource "aws_lb_target_group" "app_tg" {
  name        = "${var.TagEnv}-${var.TagProject}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 30
    interval            = 60
    path                = var.health_check_path
    port                = "traffic-port"
    protocol            = "HTTP"
  }

  tags = var.tags
}

# resource "aws_lb_listener" "app_listener" {
#   load_balancer_arn = aws_lb.app_lb.arn
#   port              = 80
#   protocol          = "HTTP"
#
#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.app_tg.arn
#   }
# }

# resource "aws_lb_listener" "app_listener_https" {
#   count             = var.enable_https ? 1 : 0
#   load_balancer_arn = aws_lb.app_lb.arn
#   port              = 443
#   protocol          = "HTTPS"
#   ssl_policy        = "ELBSecurityPolicy-2016-08"
#   certificate_arn   = var.certificate_arn
#
#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.app_tg.arn
#   }
# }
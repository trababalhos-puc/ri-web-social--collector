output "cluster_id" {
  description = "ID do cluster ECS"
  value       = aws_ecs_cluster.app_cluster.id
}

output "cluster_name" {
  description = "Nome do cluster ECS"
  value       = aws_ecs_cluster.app_cluster.name
}

# Outputs de serviço removidos
# output "service_id" {
#   description = "ID do serviço ECS"
#   value       = aws_ecs_service.app_service.id
# }
#
# output "service_name" {
#   description = "Nome do serviço ECS"
#   value       = aws_ecs_service.app_service.name
# }

output "task_definition_arn" {
  description = "ARN da task definition"
  value       = aws_ecs_task_definition.app_task.arn
}

output "schedule_rule_name" {
  description = "Nome da regra de agendamento"
  value       = aws_cloudwatch_event_rule.scheduled_task.name
}

output "schedule_expression" {
  description = "Expressão cron configurada para o agendamento"
  value       = aws_cloudwatch_event_rule.scheduled_task.schedule_expression
}

# output "alb_dns_name" {
# 	description = "DNS do Application Load Balancer"
# 	value       = aws_lb.app_lb.dns_name
# }
#
# output "alb_zone_id" {
# 	description = "Zone ID do Application Load Balancer"
# 	value       = aws_lb.app_lb.zone_id
# }
#
# output "alb_arn" {
# 	description = "ARN do Application Load Balancer"
# 	value       = aws_lb.app_lb.arn
# }

output "alb_target_group_arn" {
  description = "ARN do Target Group do ALB"
  value       = aws_lb_target_group.app_tg.arn
}
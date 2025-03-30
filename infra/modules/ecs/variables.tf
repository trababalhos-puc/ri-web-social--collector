variable "TagProject" {
  description = "Nome do projeto"
  type        = string
}

variable "TagEnv" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
}

variable "region" {
  description = "Região da AWS"
  type        = string
}

variable "tags" {
  type = map(string)
}

variable "vpc_id" {
  description = "ID da VPC"
  type        = string
}

variable "subnet_ids" {
  description = "IDs das subnets para o ECS Service"
  type        = list(string)
}

variable "task_cpu" {
  description = "Quantidade de CPU para a tarefa do ECS (em unidades)"
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "Quantidade de memória para a tarefa do ECS (em MiB)"
  type        = number
  default     = 512
}

variable "container_port" {
  description = "Porta do container"
  type        = number
  default     = 80
}

variable "service_desired_count" {
  description = "Número desejado de instâncias de tarefas"
  type        = number
  default     = 0
}

variable "assign_public_ip" {
  description = "Atribuir IP público para as tarefas"
  type        = bool
  default     = true
}

variable "health_check_path" {
  description = "Caminho para o health check"
  type        = string
  default     = "/"
}

variable "ecr_repository_url" {
  description = "URL do repositório ECR para a imagem do container"
  type        = string
}

variable "container_environment" {
  description = "Variáveis de ambiente para o container"
  type = list(object({
    name  = string
    value = string
  }))
  default = []
}

variable "enable_https" {
  description = "Habilitar HTTPS no load balancer"
  type        = bool
  default     = false
}

variable "certificate_arn" {
  description = "ARN do certificado ACM para HTTPS"
  type        = string
  default     = ""
}

variable "iam_policy_arns" {
  description = "Lista de ARNs de políticas IAM para anexar ao role de tarefa do ECS"
  type        = list(string)
  default     = []
}


variable "schedule_expression" {
  description = "Expressão cron para agendamento de execução da tarefa (ex: cron(0 12 * * ? *) para executar às 12:00 UTC diariamente)"
  type        = string
  default     = "cron(0 3 * * ? *)"
}
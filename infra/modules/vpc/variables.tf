# -*- coding: utf-8 -*-
# File name infra/modules/vpc/variables.tf

variable "TagProject" {
  type        = string
  description = "Nome do projeto"
}

variable "TagEnv" {
  type        = string
  description = "Ambiente (dev, staging, prod)"
}

variable "tags" {
  type        = map(string)
  description = "Tags adicionais para os recursos"
}

variable "region" {
  type        = string
  description = "Região da AWS"
}

variable "name_prefix" {
  description = "Prefixo para nomear os recursos da VPC"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR para a VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "az_count" {
  description = "Número de zonas de disponibilidade a serem utilizadas"
  type        = number
  default     = 2
  validation {
    condition     = var.az_count >= 2
    error_message = "O número de zonas de disponibilidade deve ser pelo menos 2."
  }
}

variable "nat_gateway_count" {
  description = "Número de NAT Gateways a serem criados (0 para nenhum, 1 para um único NAT compartilhado, ou igual ao az_count para um NAT por AZ)"
  type        = number
  default     = 1
  validation {
    condition     = var.nat_gateway_count >= 0
    error_message = "O número de NAT Gateways deve ser maior ou igual a 0."
  }
}
# -*- coding: utf-8 -*-
# File name infra/modules/vpc/outputs.tf

output "vpc_id" {
  description = "ID da VPC criada"
  value       = aws_vpc.main_vpc.id
}

output "public_subnet_ids" {
  description = "IDs das subnets públicas"
  value       = aws_subnet.public_subnets[*].id
}

output "private_subnet_ids" {
  description = "IDs das subnets privadas"
  value       = aws_subnet.private_subnets[*].id
}

output "vpc_cidr_block" {
  description = "Bloco CIDR da VPC"
  value       = aws_vpc.main_vpc.cidr_block
}

output "internet_gateway_id" {
  description = "ID do Internet Gateway"
  value       = aws_internet_gateway.igw.id
}

output "nat_gateway_ids" {
  description = "IDs dos NAT Gateways"
  value       = aws_nat_gateway.nat_gateway[*].id
}

output "nat_gateway_eips" {
  description = "IPs Elásticos dos NAT Gateways"
  value       = aws_eip.nat[*].public_ip
}
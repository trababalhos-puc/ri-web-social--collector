# -*- coding: utf-8 -*-
# File name infra/modules/vpc/main.tf

# Obter lista de zonas de disponibilidade na região
data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "main_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    var.tags,
    {
      Name = "${var.TagEnv}-${var.TagProject}-vpc"
    }
  )
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main_vpc.id

  tags = merge(
    var.tags,
    {
      Name = "${var.TagEnv}-${var.TagProject}-igw"
    }
  )
}

# Route table para subnets públicas
resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.main_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.TagEnv}-${var.TagProject}-public-rt"
    }
  )
}

# Route table para subnets privadas
resource "aws_route_table" "private_route_table" {
  vpc_id = aws_vpc.main_vpc.id

  tags = merge(
    var.tags,
    {
      Name = "${var.TagEnv}-${var.TagProject}-private-rt"
    }
  )
}

# Elastic IPs para NAT Gateways
resource "aws_eip" "nat" {
  count  = var.nat_gateway_count
  domain = "vpc"

  tags = merge(
    var.tags,
    {
      Name = "${var.TagEnv}-${var.TagProject}-nat-eip-${count.index + 1}"
    }
  )
}

# NAT Gateways
resource "aws_nat_gateway" "nat_gateway" {
  count = var.nat_gateway_count

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public_subnets[count.index].id

  tags = merge(
    var.tags,
    {
      Name = "${var.TagEnv}-${var.TagProject}-nat-gateway-${count.index + 1}"
    }
  )

  depends_on = [aws_internet_gateway.igw]
}

resource "aws_route" "private_nat_gateway" {
  count = var.nat_gateway_count > 0 ? 1 : 0

  route_table_id         = aws_route_table.private_route_table.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat_gateway[0].id
}

resource "aws_subnet" "public_subnets" {
  count                   = var.az_count
  vpc_id                  = aws_vpc.main_vpc.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    var.tags,
    {
      Name = "${var.TagEnv}-${var.TagProject}-public-subnet-${count.index + 1}"
    }
  )
}

resource "aws_subnet" "private_subnets" {
  count             = var.az_count
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + var.az_count)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge(
    var.tags,
    {
      Name = "${var.TagEnv}-${var.TagProject}-private-subnet-${count.index + 1}"
    }
  )
}

resource "aws_route_table_association" "public_route_table_association" {
  count          = var.az_count
  subnet_id      = aws_subnet.public_subnets[count.index].id
  route_table_id = aws_route_table.public_route_table.id
}

resource "aws_route_table_association" "private_route_table_association" {
  count          = var.az_count
  subnet_id      = aws_subnet.private_subnets[count.index].id
  route_table_id = aws_route_table.private_route_table.id
}
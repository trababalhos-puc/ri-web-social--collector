# -*- coding: utf-8 -*-
# File name variables.tf

variable "TagProject" {
  type = string
}

variable "TagEnv" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "creation_date" {
  type = string
}

variable "author" {
  type = string
}

locals {
  common_tags = {
    env              = var.TagEnv
    author           = "AriHenrique"
    project          = var.TagProject
    data_sensitivity = "Confidential"
    creation_date    = var.creation_date
    purpose          = "CI-CD"
    department       = "Operations"
    cost_center      = "DataOps"
    version          = "v1.0"
  }
}
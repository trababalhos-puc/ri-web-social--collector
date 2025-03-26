variable "TagProject" {
  description = "Nome do projeto"
  type = string
}

variable "TagEnv" {
  description = "Nome do ambiente"
  type = string
}

variable "aws_region" {
  description = "Regiao AWS"
  type = string
}

variable "github_acc" {
  description = "User/Organizations GitHub"
  type        = string
}


locals {
  common_tags = {
    env              = var.TagEnv
    author           = "AriHenrique"
    project          = var.TagProject
    data_sensitivity = "Confidential"
    last_update    = timestamp()
    purpose          = "CI-CD"
    department       = "Operations"
    cost_center      = "DataOps"
    version          = "v1.0"
  }
}
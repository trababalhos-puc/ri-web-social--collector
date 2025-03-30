mock_provider "aws" {}

variables {
  TagEnv       = "dev"
  TagProject   = "meu-projeto"
  bucket_names = ["dados", "logs"]
  region       = "us-east-1"

  tags = {
    Environment = "dev"
    Project     = "meu-projeto"
    Managed     = "Terraform"
  }
}

run "test_s3_bucket_creation" {
  command = plan
  module {
    source = "./modules/s3"
  }

  assert {
    condition     = length(output.name) == 2
    error_message = "Deve criar exatamente 2 buckets"
  }

  assert {
    condition     = contains(keys(output.name), "dados")
    error_message = "Bucket 'dados' não foi criado"
  }

  assert {
    condition     = contains(keys(output.name), "logs")
    error_message = "Bucket 'logs' não foi criado"
  }

  assert {
    condition = alltrue([
      for bucket_name in values(output.name) :
      can(regex("^dev-meu-projeto--[a-z0-9-]+$", bucket_name))
    ])
    error_message = "Nome do bucket não segue o formato esperado"
  }

  assert {
    condition = alltrue([
      for bucket_name in values(output.name) :
      length(bucket_name) <= 63
    ])
    error_message = "Nome do bucket excede 63 caracteres"
  }
}
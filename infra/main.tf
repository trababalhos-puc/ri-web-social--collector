

module "bucket_test" {
  source = "./modules/s3"
  TagEnv     = var.TagEnv
  TagProject = var.TagProject
  bucket_names = ["raw"]
  region     = var.aws_region
  tags = local.common_tags
}


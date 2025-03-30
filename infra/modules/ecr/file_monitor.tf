locals {
  folder    = "../${var.folder}"
  app_files = local.folder != "" ? fileset(local.folder, "**/*") : []
}

resource "null_resource" "build_and_push" {
  triggers = {
    ecr_repository_url = aws_ecr_repository.this.repository_url

    app_files_sha = length(local.app_files) > 0 ? sha256(join("", [for f in local.app_files : filesha256("${local.folder}/${f}")])) : "no-files"

    file_list = length(local.app_files) > 0 ? sha256(join(",", sort(local.app_files))) : "no-files"
  }

  count = local.folder != "" ? 1 : 0

  provisioner "local-exec" {
    command = "chmod +x ${path.module}/script.sh && ${path.module}/script.sh"
    environment = {
      FOLDER         = local.folder
      AWS_REGION     = var.region
      AWS_ACCOUNT_ID = local.aws_account_id
      ECR_REPO_NAME  = aws_ecr_repository.this.name
      IMAGE_TAG      = var.tag_image
    }
    interpreter = ["/bin/bash", "-c"]
  }
}
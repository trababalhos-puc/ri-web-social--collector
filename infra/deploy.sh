#!/bin/bash

set -e

AWS_REGION="us-east-1"
ENVIRONMENT="dev"
TFVARS_PATH="./envs/${ENVIRONMENT}/terraform.tfvars"
REPOSITORY_OWNER="AriHenrique"
REPO_CREATION_DATE=$(git log --reverse --format=%aI | head -n 1)
REPO_CREATOR=$(git log --reverse --format='%aN' | head -n 1)
REPO_NAME=$(basename `git rev-parse --show-toplevel`)


terraform init \
  -backend-config="bucket=${AWS_REGION}-${REPOSITORY_OWNER}--tfstates" \
  -backend-config="key=$(basename `git rev-parse --show-toplevel`)" \
  -backend-config="region=$AWS_REGION" \
  -backend-config="dynamodb_table=${REPOSITORY_OWNER}-${AWS_REGION}-terraform-lock"

terraform validate -no-color
terraform workspace select $ENVIRONMENT || terraform workspace new $ENVIRONMENT
terraform plan \
  -var "creation_date=$REPO_CREATION_DATE" \
  -var "author=$REPO_CREATOR" \
  -var "TagProject=$REPO_NAME" \
  -var "TagEnv=$ENVIRONMENT" \
  -var "aws_region=$AWS_REGION" \
  -var "S3Name=''" \
  -var-file="$TFVARS_PATH" \
  -out="$ENVIRONMENT.plan" \
  -no-color

terraform apply "$ENVIRONMENT.plan"

echo "Terraform deployment completed successfully!"

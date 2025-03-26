#!/bin/bash

set -e

# Destroy dos recursos do Terraform
cd infra \
  && terraform workspace select $1 \
  || terraform workspace new $1 \
  && terraform destroy \
  -var-file="./envs/$1/terraform.tfvars" \
  -auto-approve \
  -no-color

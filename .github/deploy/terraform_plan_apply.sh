#!/bin/bash

set -e

cd infra \
  && (terraform workspace select -or-create=true "$1" || terraform workspace new "$1") \
  && terraform plan \
     -var-file="./envs/$1/terraform.tfvars" \
     -out="$1.plan" \
     -no-color \
  && terraform apply "$1.plan"
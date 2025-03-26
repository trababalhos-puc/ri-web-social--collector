#!/bin/bash

set -e

# Configura o nome do bucket S3 para state files
base_name="$1-$2--tfstates"
base_repo="$3"

base_name=$(echo "$base_name" | tr '[:upper:]' '[:lower:]')
bucket_name=$(echo "$base_name" | sed -E 's/[^a-z0-9-]/-/g')
bucket_name=$(echo "$bucket_name" | sed -E 's/^-+|-+$//g' | cut -c1-63)

echo "Bucket name: $bucket_name"

repo_name=$(echo "$base_repo" | sed -E 's/[^a-zA-Z0-9-]/-/g' | sed -E 's/^-+|-+$//g' | cut -c1-63)

cd infra \
  && terraform init \
  -backend-config="bucket=$bucket_name" \
  -backend-config="key=$repo_name" \
  -backend-config="region=$1" \
  -backend-config="dynamodb_table=$2-$1-terraform-lock" \

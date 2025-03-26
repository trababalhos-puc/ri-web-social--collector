#!/bin/bash

set -e

# Esvaziar os buckets S3
buckets=$(aws s3api list-buckets --query "Buckets[?starts_with(Name, '$1') && ends_with(Name, '--art')].Name" --output text)
for bucket in $buckets; do
  aws s3 rm s3://$bucket --recursive
  echo "Esvaziado o bucket S3: $bucket"
done

# Esvaziar os repositórios ECR
repositories=$(aws ecr describe-repositories --query "repositories[?starts_with(repositoryName, '$1')].repositoryName" --output text)
for repo in $repositories; do
  images=$(aws ecr list-images --repository-name $repo --query 'imageIds[*]' --output json)
  if [ "$images" != "[]" ]; then
    aws ecr batch-delete-image --repository-name $repo --image-ids "$images"
    echo "Esvaziado o repositório ECR: $repo"
  fi
done

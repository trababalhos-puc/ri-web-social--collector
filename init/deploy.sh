#!/bin/bash

set -e


AWS_ACCOUNT=$(aws sts get-caller-identity --query "Account" --output text)
REPOSITORY_OWNER=$(echo "trababalhos-puc" | tr '[:upper:]' '[:lower:]')
AWS_REGION="us-east-1"

OIDC_PROVIDER_ARN="arn:aws:iam::$AWS_ACCOUNT:oidc-provider/token.actions.githubusercontent.com"
S3_BUCKET_NAME="${AWS_REGION}-${REPOSITORY_OWNER}--tfstates"
DYNAMODB_TABLE_NAME="${REPOSITORY_OWNER}-${AWS_REGION}-terraform-lock"
IAM_ROLE_NAME="github-actions-role-${REPOSITORY_OWNER}-${AWS_REGION}"
IAM_POLICY_NAME="github-actions-policy-${REPOSITORY_OWNER}-${AWS_REGION}"
IAM_POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT}:policy/${IAM_POLICY_NAME}"


terraform init

resource_in_state() {
  local resource_type=$1
  local resource_name=$2

  terraform state list 2>/dev/null | grep -q "${resource_type}.${resource_name}"
  return $?
}


if ! resource_in_state "aws_iam_openid_connect_provider" "github"; then
  if ! aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$OIDC_PROVIDER_ARN" &>/dev/null; then
    echo "OIDC Provider não existe, criando com Terraform..."
    terraform apply -target=aws_iam_openid_connect_provider.github -auto-approve
  else
    echo "OIDC Provider já existe, importando para o estado do Terraform..."
    terraform import aws_iam_openid_connect_provider.github "$OIDC_PROVIDER_ARN"
  fi
else
  echo "OIDC Provider já está no estado do Terraform, pulando importação..."
fi


if ! resource_in_state "aws_s3_bucket" "s3_buckets"; then
  if aws s3api head-bucket --bucket "$S3_BUCKET_NAME" &>/dev/null; then
    echo "Bucket S3 $S3_BUCKET_NAME já existe, importando para o estado do Terraform..."
    terraform import aws_s3_bucket.s3_buckets "$S3_BUCKET_NAME"
  else
    echo "Bucket S3 $S3_BUCKET_NAME não existe, será criado pelo Terraform..."
  fi
else
  echo "Bucket S3 já está no estado do Terraform, pulando importação..."
fi


if ! resource_in_state "aws_dynamodb_table" "terraform_lock"; then
  if aws dynamodb list-tables --region "$AWS_REGION" --output text | grep -q "$DYNAMODB_TABLE_NAME"; then
    echo "Tabela DynamoDB $DYNAMODB_TABLE_NAME já existe, importando para o estado do Terraform..."
    terraform import aws_dynamodb_table.terraform_lock "$DYNAMODB_TABLE_NAME"
  else
    echo "Tabela DynamoDB $DYNAMODB_TABLE_NAME não existe, será criada pelo Terraform..."
  fi
else
  echo "Tabela DynamoDB já está no estado do Terraform, pulando importação..."
fi


if ! resource_in_state "aws_iam_role" "github_actions_role"; then
  if aws iam list-roles --output text | grep -q "$IAM_ROLE_NAME"; then
    echo "IAM Role $IAM_ROLE_NAME já existe, importando para o estado do Terraform..."
    terraform import aws_iam_role.github_actions_role "$IAM_ROLE_NAME"
  else
    echo "IAM Role $IAM_ROLE_NAME não existe, será criada pelo Terraform..."
  fi
else
  echo "IAM Role já está no estado do Terraform, pulando importação..."
fi


if ! resource_in_state "aws_iam_policy" "github_actions_policy"; then
  if aws iam get-policy --policy-arn "$IAM_POLICY_ARN" &>/dev/null; then
    echo "IAM Policy $IAM_POLICY_NAME já existe, importando para o estado do Terraform..."
    terraform import aws_iam_policy.github_actions_policy "$IAM_POLICY_ARN"
  else
    echo "IAM Policy $IAM_POLICY_NAME não existe, será criada pelo Terraform..."
  fi
else
  echo "IAM Policy já está no estado do Terraform, pulando importação..."
fi

DYNAMODB_POLICY_NAME="github-actions-policy-dynamodb-${REPOSITORY_OWNER}-${AWS_REGION}"
DYNAMODB_POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT}:policy/${DYNAMODB_POLICY_NAME}"

if ! resource_in_state "aws_iam_policy" "github_actions_policy_dynamodb"; then
  if aws iam get-policy --policy-arn "$DYNAMODB_POLICY_ARN" &>/dev/null; then
    echo "IAM Policy $DYNAMODB_POLICY_NAME já existe, importando para o estado do Terraform..."
    terraform import aws_iam_policy.github_actions_policy_dynamodb "$DYNAMODB_POLICY_ARN"
  else
    echo "IAM Policy $DYNAMODB_POLICY_NAME não existe, será criada pelo Terraform..."
  fi
else
  echo "IAM Policy do DynamoDB já está no estado do Terraform, pulando importação..."
fi

echo "Gerando plano do Terraform..."
terraform plan -out=tfplan

echo "Aplicando plano do Terraform..."
terraform apply tfplan

echo "Execução do Terraform concluída com sucesso!"
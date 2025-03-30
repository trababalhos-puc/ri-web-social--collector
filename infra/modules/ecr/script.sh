#!/bin/bash
# -*- coding: utf-8 -*-
# File name modules/lambda_image/script.sh

set -e  # Exit immediately if a command exits with a non-zero status
set -x  # Print each command before executing (for debugging)

FOLDER="${FOLDER}"
AWS_REGION="${AWS_REGION}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID}"
ECR_REPO_NAME="${ECR_REPO_NAME}"
IMAGE_TAG="${IMAGE_TAG}"

echo "FOLDER - $FOLDER"
echo "AWS_REGION - $AWS_REGION"
echo "AWS_ACCOUNT_ID - $AWS_ACCOUNT_ID"
echo "ECR_REPO_NAME - $ECR_REPO_NAME"
echo "IMAGE_TAG - $IMAGE_TAG"
echo "DOCKER_BUILD_ARGS - $DOCKER_BUILD_ARGS"

ECR_REPO_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo "pasta atual"
cd "$FOLDER"
ls -a

echo "Building Docker image..."
docker build -t ${ECR_REPO_NAME} .
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${ECR_REPO_URL}:${IMAGE_TAG}

echo "Getting ECR temporary credentials..."
AUTH_TOKEN=$(aws ecr get-authorization-token --region ${AWS_REGION} --output text --query 'authorizationData[].authorizationToken')
ENDPOINT=$(aws ecr get-authorization-token --region ${AWS_REGION} --output text --query 'authorizationData[].proxyEndpoint' | sed 's|https://||')

mkdir -p /tmp/docker-auth
cat > /tmp/docker-auth/config.json << EOF
{
  "auths": {
    "${ENDPOINT}": {
      "auth": "${AUTH_TOKEN}"
    }
  }
}
EOF

export DOCKER_CONFIG=/tmp/docker-auth

echo "Using custom Docker config at: ${DOCKER_CONFIG}"
cat ${DOCKER_CONFIG}/config.json | grep -v auth

echo "Pushing with custom Docker config..."
docker --config /tmp/docker-auth push ${ECR_REPO_URL}:${IMAGE_TAG}

cd -
echo "Script completed successfully!"
#!/bin/bash

set -e

# Valida a configuração do Terraform
cd infra \
  && terraform validate \
  -no-color

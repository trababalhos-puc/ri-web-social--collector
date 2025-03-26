#!/bin/bash

set -e

cd infra \
  && terraform test \
  -no-color

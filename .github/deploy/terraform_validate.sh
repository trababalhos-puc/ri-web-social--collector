#!/bin/bash

set -e

cd infra \
  && terraform validate \
  -no-color

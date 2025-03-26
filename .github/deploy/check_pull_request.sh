#!/bin/bash

set -e

# Verifica se existe uma PR aberta para este branch
pr=$(gh pr list --state open --head "$1" --json number --jq '.[0].number')

if [ -n "$pr" ]; then
  # Existe uma PR para este branch
  if [ "$2" == "pull_request" ]; then
    echo "should_run_terraform=true" >> $GITHUB_ENV
  else
    echo "should_run_terraform=false" >> $GITHUB_ENV
  fi
else
  echo "should_run_terraform=true" >> $GITHUB_ENV
fi

echo "should_run_terraform=$should_run_terraform" >> $GITHUB_OUTPUT

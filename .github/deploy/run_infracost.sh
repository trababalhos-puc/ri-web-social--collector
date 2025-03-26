#!/bin/bash

set -e

# Configura e executa o Infracost
infracost configure set api_key $1
git fetch --unshallow
infracost breakdown --path . > infracost_output.txt
echo "cost_summary_file=infracost_output.txt" >> $GITHUB_ENV
echo "::set-output name=cost_summary_file::infracost_output.txt"

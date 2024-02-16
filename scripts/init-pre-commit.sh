#!/bin/sh

echo "Install pre-commit hook"
pre-commit install
echo "Run pre-commit hooks"
cd "../" && pwd && pre-commit run --all-files
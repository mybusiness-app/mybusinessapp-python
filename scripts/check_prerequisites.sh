#!/bin/bash

echo "Checking prerequisites..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"
IFS='.' read -r -a version_parts <<< "$python_version"
if [[ ${version_parts[0]} -lt 3 || ( ${version_parts[0]} -eq 3 && ${version_parts[1]} -lt 13 ) ]]; then
    echo "❌ Python 3.13+ is required"
    exit 1
fi
echo "✅ Python version check passed"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi
echo "✅ Docker is installed"

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed"
    exit 1
fi
echo "✅ Azure CLI is installed"

# Check if logged into Azure
if ! az account show &> /dev/null; then
    echo "❌ Not logged into Azure. Please run 'az login'"
    exit 1
fi
echo "✅ Azure CLI is authenticated"

echo "All prerequisites are satisfied! 🎉"
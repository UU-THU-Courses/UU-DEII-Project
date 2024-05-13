#!/bin/bash

GIT_REPO="https://github.com/bytedeco/javacv.git"
[ ! -z "$1" ] && GIT_REPO="$1"

# Download the Repository
# from GitHub
git clone ${GIT_REPO} testRepo

# Change directory
cd testRepo

# Run tests
mvn test

# Check outputs
python3 /worker/process.py --path="target/surefire-reports"
#!/bin/bash

GIT_REPO="https://github.com/bytedeco/javacv.git"
OUT_PATH="/testRepo"
[ ! -z "$1" ] && GIT_REPO="$1"
[ ! -z "$2" ] && OUT_PATH="$2"

# Download the Repository
# from GitHub
git clone ${GIT_REPO} ${OUT_PATH}

# Change directory
cd ${OUT_PATH}

# Run maven tests
mvn test

# Check outputs
# python3 /worker/process.py --path="target/surefire-reports"
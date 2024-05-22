#!/bin/bash

config_file="configs/deploy-cfg.yaml"
[ ! -z "$1" ] && config_file="$1"

# Start deployment
python3 deploy.py --full --config_file=${config_file}

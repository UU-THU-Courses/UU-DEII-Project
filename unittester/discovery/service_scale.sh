#!/bin/bash

add_count=8
[ ! -z "$1" ] && add_count="$1"

# Fetch current replica count
# for worker containers
replicas=$(docker service inspect --format '{{.Spec.Mode.Replicated.Replicas}}' unittester_worker)

# Update the replica count
((replicas+=add_count))

# Scale the worker service
docker service scale unittester_worker=${replicas} -d
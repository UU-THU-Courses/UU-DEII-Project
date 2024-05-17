#!/bin/bash

# Fetch current replica count
# for worker containers
replicas=$(docker service inspect --format '{{.Spec.Mode.Replicated.Replicas}}' unittester_worker)

# Update the replica count
((replicas+=5))

# Scale the worker service
docker service scale unittester_worker=${replicas} -d
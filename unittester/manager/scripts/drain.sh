#!/bin/bash

drain_count=1
log_filename="logfile.txt"
[ ! -z "$1" ] && drain_count="$1"
[ ! -z "$2" ] && log_filename="$2"

worker_nodes=$(docker node inspect --format '{{.Description.Hostname}}' $(docker node ls --filter role="worker" -q))
worker_count=$(docker node inspect --format '{{.Description.Hostname}}' $(docker node ls --filter role="worker" -q) | wc -l)
n_containers=$(docker service inspect --format '{{.Spec.Mode.Replicated.Replicas}}' unittester_worker)

printf "# of worker nodes: ${worker_count}\n"

# Convert the docker response to an array
readarray -t  worker_nodes <<<"${worker_nodes}"

if [ "${drain_count} " -le "${worker_count}" ]; then
    # Scale down first before doing anything else
    for ((idx=${#worker_nodes[@]}-1,count=drain_count; idx>=0 && count>0; idx--,count--)) ; do
        # Check the number of containers running on current node
        container_count=$(docker node ps --format "{{.ID}}" --filter "desired-state=running" ${worker_nodes[idx]} | wc -l)
        # Update the n_containers that should be running after
        # the node has been drained
        ((n_containers-=container_count))
    done
    
    # Scale down the number of worker containers
    docker service scale unittester_worker=${n_containers} -d

    for ((idx=${#worker_nodes[@]}-1,count=drain_count; idx>=0 && count>0; idx--,count--)) ; do
        printf "Draining: ${worker_nodes[idx]}\n"
        # Set the node availability to drain
        docker node update --availability drain ${worker_nodes[idx]}
        # Remove the node??
        docker node rm --force ${worker_nodes[idx]}
        # Log the node name to a file
        printf "${worker_nodes[idx]}\n" >> ${log_filename}
    done
else
    printf "Error: Drain count ${drain_count} cannot be greater than active workers ${worker_count}.\n"
fi
#!/bin/bash

drain_count=1
log_filename="logfile.txt"
[ ! -z "$1" ] && drain_count="$1"
[ ! -z "$2" ] && log_filename="$2"

worker_nodes=$(docker node inspect --format '{{.Description.Hostname}}' $(docker node ls --filter role="worker" -q))
worker_count=$(docker node inspect --format '{{.Description.Hostname}}' $(docker node ls --filter role="worker" -q) | wc -l)

printf "Worker nodes: ${worker_count}\n"

# Convert the docker response to an array
readarray -t  worker_nodes <<<"${worker_nodes}"

if [ "${drain_count} " -le "${worker_count}" ]; then
        for ((idx=${#worker_nodes[@]}-1,count=drain_count; idx>=0 && count>0; idx--, count--)) ; do
            printf "Draining: ${worker_nodes[idx]}\n"
            # Set the node availability to drain
            # docker node update --availability drain ${worker_nodes[idx]}
            # Scale down the number of worker containers
            # Log the node name to a file
            printf "${worker_nodes[idx]}\n" >> ${log_filename}
        done
else
        printf "Error: Drain count ${drain_count} cannot be greater than active workers ${worker_count}.\n"
fi
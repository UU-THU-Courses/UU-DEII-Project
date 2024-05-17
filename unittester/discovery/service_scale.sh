#!/bin/bash

nodes=$(docker node ls -q)
container_count=0
for node in ${nodes[@]}
do
        containers=$(docker node ps ${node} --filter "name=unittester_worker" --filter "desired-state=Running" -q | wc -l)
        ((container_count+=containers))
done

echo "Old container count: ${container_count}"
((container_count+=5))
echo "New container count: ${container_count}"

docker service scale unittester_worker=${container_count} -d
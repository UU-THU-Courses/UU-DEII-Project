#!/bin/bash

declar -i container_count
container_count=$(docker service ls --filter name=worker -q | wc -l)

((container_count+=5))
docker service scale worker=${existing_containers} -d

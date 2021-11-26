#!/bin/sh
docker-compose -p "Invidia-Prod" --env-file ~/deploy/envs/invidia-env up -d
docker-compose -p "Valk-Prod" --env-file ~/deploy/envs/valk-env up -d
docker-compose -p "Ethereal-Prod" --env-file ~/deploy/envs/ethereal-env up -d

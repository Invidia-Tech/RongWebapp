#!/bin/sh
docker-compose -p "Invidia-Prod" --env-file ~/deploy/envs/invidia-env up -d
docker-compose -p "Valk-Prod" --env-file ~/deploy/envs/valk-env up -d
docker-compose -p "Ethereal-Prod" --env-file ~/deploy/envs/ethereal-env up -d
docker-compose -p "PA-Prod" --env-file ~/deploy/envs/pa-env up -d
docker-compose -p "Midnight-Prod" --env-file ~/deploy/envs/midnight-env up -d

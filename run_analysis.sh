#!/bin/bash

# Build and run inside Docker container
docker-compose build
docker-compose run opteran_analyser python3 /workspace/scripts/analyse_localisation.py

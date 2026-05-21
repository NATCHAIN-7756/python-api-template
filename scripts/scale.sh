#!/bin/bash
# Scale Script - Add/Remove API Containers
# SCALE OS v10.0

set -e

ACTION=${1:-"status"}
COUNT=${2:-3}

case $ACTION in
    up)
        echo "Scaling up to $COUNT API containers..."
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale api=$COUNT
        ;;
    down)
        echo "Scaling down to $COUNT API containers..."
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale api=$COUNT
        ;;
    status)
        echo "Current container status:"
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
        ;;
    *)
        echo "Usage: $0 {up|down|status} [count]"
        echo "  up     - Scale up to specified count (default: 3)"
        echo "  down   - Scale down to specified count"
        echo "  status - Show current container status"
        exit 1
        ;;
esac

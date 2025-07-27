#!/bin/bash
# Docker deployment script for diet server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_warning "Docker Compose not found. Using 'docker compose' instead."
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Function to build the Docker image
build_image() {
    print_status "Building Docker image..."
    docker build -t diet-server:latest .
    print_status "Docker image built successfully!"
}

# Function to run with Docker Compose
run_compose() {
    print_status "Starting services with Docker Compose..."
    $DOCKER_COMPOSE up -d
    print_status "Services started! Check status with: $DOCKER_COMPOSE ps"
    print_status "API available at: http://localhost:8000"
    print_status "API docs available at: http://localhost:8000/docs"
}

# Function to run with Docker Compose including nginx
run_compose_nginx() {
    print_status "Starting services with nginx reverse proxy..."
    $DOCKER_COMPOSE --profile with-nginx up -d
    print_status "Services started with nginx proxy!"
    print_status "API available at: http://localhost"
    print_status "Direct API access: http://localhost:8000"
    print_status "API docs available at: http://localhost/docs"
}

# Function to run simple Docker container
run_simple() {
    print_status "Running simple Docker container..."
    docker run -d --name diet-server -p 8000:8000 diet-server:latest
    print_status "Container started!"
    print_status "API available at: http://localhost:8000"
    print_status "API docs available at: http://localhost:8000/docs"
}

# Function to stop services
stop_services() {
    print_status "Stopping Docker services..."
    $DOCKER_COMPOSE down
    docker stop diet-server 2>/dev/null || true
    docker rm diet-server 2>/dev/null || true
    print_status "Services stopped!"
}

# Function to view logs
show_logs() {
    if $DOCKER_COMPOSE ps | grep -q diet-server; then
        $DOCKER_COMPOSE logs -f diet-server
    elif docker ps | grep -q diet-server; then
        docker logs -f diet-server
    else
        print_error "No running diet-server container found!"
    fi
}

# Function to show status
show_status() {
    print_status "Docker Compose services:"
    $DOCKER_COMPOSE ps
    echo ""
    print_status "Docker containers:"
    docker ps --filter "name=diet-server"
}

# Main script logic
case "${1:-}" in
    "build")
        build_image
        ;;
    "run")
        build_image
        run_compose
        ;;
    "run-nginx")
        build_image
        run_compose_nginx
        ;;
    "run-simple")
        build_image
        run_simple
        ;;
    "stop")
        stop_services
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "restart")
        stop_services
        sleep 2
        run_compose
        ;;
    *)
        echo "Usage: $0 {build|run|run-nginx|run-simple|stop|logs|status|restart}"
        echo ""
        echo "Commands:"
        echo "  build      - Build Docker image"
        echo "  run        - Build and run with Docker Compose"
        echo "  run-nginx  - Build and run with nginx reverse proxy"
        echo "  run-simple - Build and run simple Docker container"
        echo "  stop       - Stop all services"
        echo "  logs       - Show application logs"
        echo "  status     - Show service status"
        echo "  restart    - Restart services"
        exit 1
        ;;
esac

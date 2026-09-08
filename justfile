# Project recipes

# Default recipe
_default:
    @just --list --unsorted

# Build the Docker images in a specified directory
build directory:
    @python3 ./generate_base_images.py {{ directory }}

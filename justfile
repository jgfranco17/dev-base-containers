# Project recipes

# Default recipe
_default:
    @just --list --unsorted

# Build the Docker images in a specified directory
build *args:
    @uv run python3 generate_base_images.py {{ args }}

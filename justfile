# Project recipes

# Default recipe
_default:
    @just --list --unsorted

# Setup development environment
install:
    #!/usr/bin/env bash
    if [ $(command -v uv >/dev/null 2>&1) ]; then
        echo "WARNING: uv is not installed, please install it first."
        echo "Docs: https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
    echo "Setting up project workspace..."
    if [[ ! -d .venv ]]; then
        echo "No virtual environment found, creating a new one..."
        uv venv
        echo "Virtual environment created."
    fi
    uv sync
    echo "Project workspace setup complete!"
    echo "NOTE: Remember to activate the virtual environment before running other commands."

# Build the Docker images in a specified directory
imvar-cli *args:
    @uv run imvar-cli {{ args }}

# Run the Python test suite
pytest *args:
    @uv run pytest {{ args }}

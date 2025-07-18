#!/bin/bash

# Setup script for testing environment
# This script sets up the testing environment with all necessary tools

set -e  # Exit on any error

echo "🚀 Setting up testing environment for spec-driven-agent..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "🔧 Installing development dependencies..."
pip install -e ".[dev]"

# Install pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
pre-commit install

# Install pre-commit hooks for all stages
echo "🔗 Installing pre-commit hooks for all stages..."
pre-commit install --hook-type pre-commit
pre-commit install --hook-type pre-push

# Create test directories if they don't exist
echo "📁 Creating test directories..."
mkdir -p tests/unit/test_agents
mkdir -p tests/unit/test_models
mkdir -p tests/unit/test_core
mkdir -p tests/unit/test_cli
mkdir -p tests/integration
mkdir -p tests/fixtures
mkdir -p tests/utils

# Create __init__.py files if they don't exist
touch tests/unit/__init__.py
touch tests/unit/test_agents/__init__.py
touch tests/unit/test_models/__init__.py
touch tests/unit/test_core/__init__.py
touch tests/unit/test_cli/__init__.py
touch tests/integration/__init__.py
touch tests/fixtures/__init__.py
touch tests/utils/__init__.py

# Run initial tests to verify setup
echo "🧪 Running initial tests to verify setup..."
pytest tests/unit/ -v --tb=short

# Run pre-commit on all files
echo "🔍 Running pre-commit on all files..."
pre-commit run --all-files

echo "✅ Testing environment setup complete!"
echo ""
echo "📋 Available commands:"
echo "  pytest tests/unit/ -v          # Run unit tests"
echo "  pytest tests/integration/ -v    # Run integration tests"
echo "  pytest --cov=spec_driven_agent  # Run tests with coverage"
echo "  pre-commit run --all-files      # Run all pre-commit hooks"
echo "  black .                         # Format code"
echo "  isort .                         # Sort imports"
echo "  flake8 .                        # Lint code"
echo "  mypy spec_driven_agent/         # Type check"
echo ""
echo "🎯 Happy testing!"

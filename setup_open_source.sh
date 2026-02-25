#!/bin/bash
# Setup script for Nexus Open Source Agent
# Installs Ollama, downloads models, prepares environment

echo "🚀 Setting up Nexus Open Source Agent..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Pull Llama 3.1 model
echo "🦙 Downloading Llama 3.1 (8B)..."
ollama pull llama3.1:8b

# Create directories
mkdir -p knowledge
mkdir -p chroma_db
mkdir -p storage

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install -r requirements-open-source.txt

echo "✅ Setup complete!"
echo ""
echo "To start the agent:"
echo "  python agent_v3_open_source.py"
echo ""
echo "To add knowledge:"
echo "  Put .txt files in ./knowledge/ directory"
echo "  They'll be indexed automatically on first run"

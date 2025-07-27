#!/bin/bash

echo "============================================"
echo "Super Productivity MCP Bridge Setup"
echo "============================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not installed or not in PATH"
    echo "Please ensure pip3 is installed with Python"
    exit 1
fi

echo "Installing MCP dependencies..."
pip3 install mcp

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install MCP dependencies"
    exit 1
fi

# Create data directory
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    MCP_DIR="$HOME/Library/Application Support/super-productivity-mcp"
else
    # Linux
    MCP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/super-productivity-mcp"
fi

echo "Creating MCP directory: $MCP_DIR"
mkdir -p "$MCP_DIR"
mkdir -p "$MCP_DIR/plugin_commands"
mkdir -p "$MCP_DIR/plugin_responses"

# Copy MCP server to data directory (from parent directory)
echo "Copying MCP server and setting execution permissions..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/../mcp_server.py" "$MCP_DIR/mcp_server.py"
cp "$SCRIPT_DIR/../merge_config.py" "$MCP_DIR/merge_config.py"
chmod +x "$MCP_DIR/mcp_server.py"
chmod +x "$MCP_DIR/merge_config.py"

echo
echo "============================================"
echo "MCP Server Setup Complete!"
echo "============================================"
echo

# Ask about Claude Desktop setup
read -p "Do you want to configure Claude Desktop? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Setting up Claude Desktop..."
    bash "$SCRIPT_DIR/setup-claude.sh" "$MCP_DIR"
else
    echo "Skipping Claude Desktop setup."
fi

echo

# Ask about Open Code setup
read -p "Do you want to configure Open Code? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Setting up Open Code..."
    bash "$SCRIPT_DIR/setup-opencode.sh" "$MCP_DIR"
else
    echo "Skipping Open Code setup."
fi

echo
echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo
echo "Next steps:"
echo "1. Install the plugin in Super Productivity:"
echo "   - Open Super Productivity"
echo "   - Go to Settings > Plugins"
echo "   - Click \"Upload Plugin\""
echo "   - Select the sp-mcp-bridge-v*.zip file from the parent folder"
echo
echo "2. Activate the plugin in the Super Productivity settings"
echo
echo "3. Test the integration by asking your AI assistant to:"
echo "   \"Create a task in Super Productivity\""
echo
echo "MCP Server installed at: $MCP_DIR"
echo
echo "Press Enter to exit..."
read
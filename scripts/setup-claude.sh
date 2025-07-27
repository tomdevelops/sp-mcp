#!/bin/bash

MCP_DIR="$1"

if [ -z "$MCP_DIR" ]; then
    echo "ERROR: MCP directory not provided"
    exit 1
fi

echo "Configuring Claude Desktop..."

# Determine Claude config location
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
else
    # Linux
    CLAUDE_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/Claude/claude_desktop_config.json"
fi

# Create Claude config directory if it doesn't exist
mkdir -p "$(dirname "$CLAUDE_CONFIG")"

# Check if config file exists and merge
if [ -f "$CLAUDE_CONFIG" ]; then
    echo "Backing up existing Claude config..."
    cp "$CLAUDE_CONFIG" "$CLAUDE_CONFIG.backup"

    echo "Adding super-productivity to existing MCP servers..."
    echo "Merging with existing Claude Desktop configuration..."

    python3 "$MCP_DIR/merge_config.py" "$CLAUDE_CONFIG" "$MCP_DIR"

    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to merge configuration. Your backup is at $CLAUDE_CONFIG.backup"
        echo "Please manually add this to your Claude Desktop config:"
        echo
        echo '  "super-productivity": {'
        echo '    "command": "python3",'
        echo '    "args": ["'$MCP_DIR'/mcp_server.py"]'
        echo '  }'
        echo
        exit 1
    fi
else
    echo "Creating new Claude Desktop configuration..."
    cat > "$CLAUDE_CONFIG" << EOF
{
  "mcpServers": {
    "super-productivity": {
      "command": "python3",
      "args": ["$MCP_DIR/mcp_server.py"]
    }
  }
}
EOF
fi

echo "✓ Claude Desktop configuration updated at: $CLAUDE_CONFIG"
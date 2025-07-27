#!/bin/bash

MCP_DIR="$1"

if [ -z "$MCP_DIR" ]; then
    echo "ERROR: MCP directory not provided"
    exit 1
fi

echo "Configuring OpenCode..."

# Determine OpenCode config location
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    OPENCODE_CONFIG="$HOME/Library/Application Support/opencode/opencode.json"
else
    # Linux
    OPENCODE_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/opencode.json"
fi

# Create OpenCode config directory if it doesn't exist
mkdir -p "$(dirname "$OPENCODE_CONFIG")"

# Check if config file exists and merge
if [ -f "$OPENCODE_CONFIG" ]; then
    echo "Backing up existing OpenCode config..."
    cp "$OPENCODE_CONFIG" "$OPENCODE_CONFIG.backup"

    echo "Adding super-productivity to existing MCP servers..."
    echo "Merging with existing OpenCode configuration..."

    python3 "$MCP_DIR/merge_config.py" "$OPENCODE_CONFIG" "$MCP_DIR"

    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to merge configuration. Your backup is at $OPENCODE_CONFIG.backup"
        echo "Please manually add this to your OpenCode config.json:"
        echo
        echo '  "mcp": {'
        echo '    "super-productivity": {'
        echo '      "type": "local",'
        echo '      "command": ["python3", "'$MCP_DIR'/mcp_server.py"],'
        echo '      "enabled": true'
        echo '    }'
        echo '  }'
        echo
        exit 1
    fi
else
    echo "Creating new OpenCode configuration..."
    cat > "$OPENCODE_CONFIG" << EOF
{
  "\$schema": "https://opencode.ai/config.json",
  "mcp": {
    "super-productivity": {
      "type": "local",
      "command": [
        "python3",
        "$MCP_DIR/mcp_server.py"
      ],
      "enabled": true
    }
  }
}
EOF
fi

echo "✓ OpenCode configuration updated at: $OPENCODE_CONFIG"
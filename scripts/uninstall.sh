#!/bin/bash

# Super Productivity MCP Server Uninstaller
# This script reverts all changes made by setup.sh

set -e

echo "🗑️  Uninstalling Super Productivity MCP Server..."

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
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERR]${NC} $1"
}

# Check if running on macOS or Linux and set config paths
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
    CLAUDE_CONFIG="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
    OPENCODE_CONFIG_DIR="$HOME/.config/opencode/"
    OPENCODE_CONFIG="$OPENCODE_CONFIG_DIR/opencode.json"

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
    CLAUDE_CONFIG="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
    OPENCODE_CONFIG_DIR="$HOME/.config/opencode/"
    OPENCODE_CONFIG="$OPENCODE_CONFIG_DIR/opencode.json"
else
    print_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

remove_mcp_config() {
    local config_removed=false

    # Remove from Claude configuration
    if [ -f "$CLAUDE_CONFIG" ]; then
        print_status "Removing MCP server configuration from Claude..."

        # Create backup of current config
        cp "$CLAUDE_CONFIG" "${CLAUDE_CONFIG}.uninstall.backup.$(date +%Y%m%d_%H%M%S)"
        print_status "Backup created: ${CLAUDE_CONFIG}.uninstall.backup.$(date +%Y%m%d_%H%M%S)"

        # Remove the super-productivity-mcp server entry using jq
        if command -v jq >/dev/null 2>&1; then
            # Use jq to remove the server entry
            jq 'del(.mcpServers."super-productivity")' "$CLAUDE_CONFIG" > "${CLAUDE_CONFIG}.tmp" && mv "${CLAUDE_CONFIG}.tmp" "$CLAUDE_CONFIG"
            print_status "✅ MCP server configuration removed from Claude"
            config_removed=true
        else
            print_warning "jq not found. You may need to manually remove the super-productivity-mcp entry from $CLAUDE_CONFIG"
        fi
    else
        print_warning "Claude config file not found at $CLAUDE_CONFIG"
    fi

    # Remove from OpenCode configuration
    if [ -f "$OPENCODE_CONFIG" ]; then
        print_status "Removing MCP server configuration from OpenCode..."

        # Create backup of current config
        cp "$OPENCODE_CONFIG" "${OPENCODE_CONFIG}.uninstall.backup.$(date +%Y%m%d_%H%M%S)"
        print_status "Backup created: ${OPENCODE_CONFIG}.uninstall.backup.$(date +%Y%m%d_%H%M%S)"

        # Remove the super-productivity-mcp server entry using jq
        if command -v jq >/dev/null 2>&1; then
            # Use jq to remove the server entry
            jq 'del(.mcp."super-productivity")' "$OPENCODE_CONFIG" > "${OPENCODE_CONFIG}.tmp" && mv "${OPENCODE_CONFIG}.tmp" "$OPENCODE_CONFIG"
            print_status "✅ MCP server configuration removed from OpenCode"
            config_removed=true
        else
            print_warning "jq not found. You may need to manually remove the super-productivity entry from $OPENCODE_CONFIG"
        fi
    else
        print_warning "OpenCode config file not found at $OPENCODE_CONFIG"
    fi

    if [ "$config_removed" = false ]; then
        print_warning "No MCP configurations found to remove"
    fi
}

remove_data_directories() {
    # Determine data directory based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        DATA_DIR="$HOME/Library/Application Support/super-productivity-mcp"
    else
        # Linux
        DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/super-productivity-mcp"
    fi

    if [ -d "$DATA_DIR" ]; then
        print_status "Removing MCP data directory at $DATA_DIR..."
        read -p "Are you sure you want to remove all MCP data? This cannot be undone. (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$DATA_DIR"
            print_status "✅ MCP data directory removed"
        else
            print_warning "Skipped removing MCP data directory"
        fi
    else
        print_warning "MCP data directory not found at $DATA_DIR"
    fi
}

# Main uninstallation process
print_status "Starting uninstallation process..."

remove_mcp_config
remove_data_directories

echo ""
print_status "🎉 Uninstallation completed!"
echo ""
print_status "The following items have been removed/reverted:"
print_status "✅ MCP server configuration from Claude and OpenCode (if found)"
print_warning "Note: The project files in $(pwd) have been kept."
print_warning "If you want to completely remove the project, delete this directory manually."
print_status "To reinstall, run: ./setup.sh"
import json
import sys
import os


def merge_claude_config(config_file, mcp_dir):
    backup_file = config_file + '.backup'

    try:
        # Load existing config if it exists
        config = {}
        if os.path.exists(backup_file):
            with open(backup_file, 'r') as f:
                config = json.load(f)
        elif os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)

        # Ensure mcpServers exists
        if 'mcpServers' not in config:
            config['mcpServers'] = {}

        # Add or update super-productivity server
        config['mcpServers']['super-productivity'] = {
            'command': 'python',
            'args': [os.path.join(mcp_dir, 'mcp_server.py')]
        }

        # Write back the merged config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        print('Successfully merged Super Productivity MCP server into existing configuration')
        return True

    except Exception as e:
        print(f'Error merging config: {e}')
        return False

def merge_opencode_config(config_file, mcp_dir):
    backup_file = config_file + '.backup'

    try:
        # Load existing config if it exists
        config = {}
        if os.path.exists(backup_file):
            with open(backup_file, 'r') as f:
                config = json.load(f)
        elif os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)

        # Ensure schema and mcp sections exist
        if '$schema' not in config:
            config['$schema'] = 'https://opencode.ai/config.json'

        if 'mcp' not in config:
            config['mcp'] = {}

        # Add or update super-productivity server
        config['mcp']['super-productivity'] = {
            'type': 'local',
            'command': [
                'python3',
                os.path.join(mcp_dir, 'mcp_server.py')
            ],
            'enabled': True
        }

        # Write back the merged config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        print('Successfully merged Super Productivity MCP server into existing Open Code configuration')
        return True

    except Exception as e:
        print(f'Error merging Open Code config: {e}')
        return False


def detect_config_type(config_file):
    """Detect whether the config file is for Claude or Open Code"""

    # First check by file path
    if 'claude' in config_file.lower():
        return 'claude'
    elif 'opencode' in config_file.lower() or 'open-code' in config_file.lower():
        return 'opencode'

    return None


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python merge_config.py <config_file> <mcp_dir>')
        sys.exit(1)

    config_file = sys.argv[1]
    mcp_dir = sys.argv[2]

    config_type = detect_config_type(config_file)

    if config_type is None:
        print(f'Could not detect config type from {config_file}. Please ensure it is a valid Claude or Open Code config file.')
        sys.exit(1)

    if config_type == 'opencode':
        print(f'Detected Open Code config: {config_file}')
        success = merge_opencode_config(config_file, mcp_dir)
    elif config_type == 'claude':
        print(f'Detected Claude config: {config_file}')
        success = merge_claude_config(config_file, mcp_dir)
    else:
        print(f'Unknown config type for {config_file}. Please ensure it is a valid Claude or Open Code config file.')
        sys.exit(1)

    sys.exit(0 if success else 1)
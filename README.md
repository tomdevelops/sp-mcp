# SP-MCP

Bridge between the amazing [Super Productivity](https://github.com/johannesjo/super-productivity/) app and MCP (Model Context Protocol) servers for AI assistant integration.

This MCP server and plugin allows AI assistants like Claude Desktop and many more to directly interact with Super Productivity through the MCP protocol. Create, update tasks, manage projects and tags, and get information from Super Productivity.

Make sure to backup your Super Productivity before using in case of data loss. I've provided a plugin.zip for convenience but feel free to make your own from the files.

(Can't delete tasks right now (but it can mark them as done))

## Demo

https://github.com/user-attachments/assets/cc118173-023f-48cb-8213-427027e475af


## Requirements

- Super Productivity 14.0.0 or higher
- MCP-compatible AI assistant (Claude Desktop, Open Code, etc.)
- Python 3.8 or higher

## Installation

### Automatic Setup

**Windows UNTESTED:**
1. Clone this repo
2. Navigate to the `scripts` folder
3. Run `setup.bat`
4. Choose which MCP clients to configure (Claude Desktop, Open Code)
5. Follow the prompts

**Linux/Mac:**
1. Clone this repo
2. Navigate to the `scripts` folder
3. Run `chmod +x setup.sh && ./setup.sh`
4. Choose which MCP clients to configure (Claude Desktop, Open Code)
5. Follow the prompts

The setup scripts will:
- Install Python dependencies
- Set up the MCP server in the appropriate data directory
- Preserve any existing MCP server configurations
- Configure your chosen AI assistants (Claude Desktop, Open Code)

You'll still need to install the plugin manually in Super Productivity (Settings → Plugins → Upload Plugin → select `sp-mcp-bridge-v*.zip`).

Once that's done, restart your configured AI assistants and Super Productivity, and you should be able to interact with your tasks.

### Manual Setup

1. **Install Python dependencies:**
   ```bash
   pip install mcp
   ```

2. **Set up MCP server:**
   Copy `mcp_server.py` to your data directory:
   - Windows: `%APPDATA%\super-productivity-mcp\`
   - Linux: `~/.local/share/super-productivity-mcp/`
   - macOS: `~/Library/Application Support/super-productivity-mcp/`

3. **Configure AI Assistants:**

   **Claude Desktop:**
   Edit Claude's config file and add to `mcpServers`:
   ```json
   "super-productivity": {
     "command": "python3",
     "args": ["/path/to/mcp_server.py"]
   }
   ```

   **Open Code:**
   Edit Open Code's config file and add to `mcp`:
   ```json
   "super-productivity": {
     "type": "local",
     "command": ["python3", "/path/to/mcp_server.py"],
     "enabled": true
   }
   ```

4. **Install the plugin:**
   - Open Super Productivity → Settings → Plugins
   - Click "Upload Plugin"
   - Select `sp-mcp-bridge-v*.zip`

5. **Restart your AI assistant (Claude Desktop, Open Code, etc.)**

## Uninstallation

### Automatic Uninstall

**Windows:**
1. Navigate to the `scripts` folder
2. Run `uninstall.bat`
3. Follow the prompts to remove configurations and data

**Linux/Mac:**
1. Navigate to the `scripts` folder
2. Run `chmod +x uninstall.sh && ./uninstall.sh`
3. Follow the prompts to remove configurations and data

The uninstall scripts will:
- Remove MCP server configurations from Claude Desktop and Open Code
- Create backups of existing configurations before removal
- Optionally remove MCP data directories
- Keep the project files (you can delete them manually if desired)

### Manual Uninstall

1. **Remove MCP configurations:**
   - **Claude Desktop:** Remove the `"super-productivity"` entry from `mcpServers` in the config file
   - **Open Code:** Remove the `"super-productivity"` entry from `mcp` in the config file

2. **Remove data directories:**
   - Windows: `%APPDATA%\super-productivity-mcp\`
   - Linux: `~/.local/share/super-productivity-mcp/`
   - macOS: `~/Library/Application Support/super-productivity-mcp/`

3. **Remove plugin from Super Productivity:**
   - Go to Settings → Plugins
   - Find the SP-MCP Bridge plugin and remove it

## Usage

### Creating Tasks
```
"Create a task to review the quarterly budget #finance +work"
```

### Task Management
```
"Show me all my tasks"
"Mark the budget review task as complete"
"Update the task 'Meeting prep' with notes about the agenda"
```

### Project and Tag Management
```
"Create a new project called 'Website Redesign'"
"Show me all projects"
"Get all tags"
```

## Dashboard

Access the SP-MCP dashboard from the menu. The dashboard shows:
- Real-time statistics
- Connection status
- Activity logs
- Settings (polling frequency: default 2 seconds)

## Communication

The plugin uses file-based communication through:
- Windows: `%APPDATA%\super-productivity-mcp\`
- Linux: `~/.local/share/super-productivity-mcp/`
- macOS: `~/Library/Application Support/super-productivity-mcp/`

Commands are exchanged through `plugin_commands/` and `plugin_responses/` directories.

## Troubleshooting

### Plugin Not Loading
- Check Super Productivity version (14.0.0+ required)
- Verify plugin permissions include `nodeExecution`

### Commands Not Working
- Verify both plugin and MCP server are running
- Check file permissions on communication directories
- Check `mcp_server.log` in the data directory

## Building

To build the zip plugin package:

```bash
bash scripts/build-plugin.sh
```

This will create a zip file named `{plugin-id}-v{version}.zip` in the project root, containing all the necessary plugin files.

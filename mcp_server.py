#!/usr/bin/env python3
# MCP Server for Super Productivity Integration

import asyncio
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions


class SuperProductivityMCPServer:
    def __init__(self):
        self.server = Server("super-productivity")
        self.setup_directories()
        self.setup_logging()
        self.setup_tools()

    def setup_directories(self):
        if os.name == 'nt':  # Windows
            data_dir = os.environ.get('APPDATA', os.path.expanduser('~/AppData/Roaming'))
        else:  # Linux/Mac
            data_dir = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))

        self.base_dir = Path(data_dir) / 'super-productivity-mcp'
        self.command_dir = self.base_dir / 'plugin_commands'
        self.response_dir = self.base_dir / 'plugin_responses'

        # Create directories
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.command_dir.mkdir(parents=True, exist_ok=True)
        self.response_dir.mkdir(parents=True, exist_ok=True)

        print(f"MCP Server using directory: {self.base_dir}", file=sys.stderr)
        print(f"Command directory: {self.command_dir}", file=sys.stderr)
        print(f"Response directory: {self.response_dir}", file=sys.stderr)


    def setup_logging(self):
        log_file = self.base_dir / 'mcp_server.log'
        try:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler(sys.stderr)
                ],
                force=True  # Force reconfiguration of logging
            )
            # Test that logging works
            logging.info(f"Logging initialized successfully. Log file: {log_file}")
        except Exception as e:
            print(f"Failed to setup logging: {e}", file=sys.stderr)
            # Fallback to basic stderr logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler(sys.stderr)],
                force=True
            )

    def setup_tools(self):
        """Set up MCP tools"""

        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="create_task",
                    description="Create a new task in Super Productivity. When users provide natural language with time/date references, convert them to Super Productivity syntax in the title field.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title with Super Productivity syntax. Convert natural language time/date references to @syntax using days/weeks/months from TODAY (e.g., 'tomorrow' -> '@1days', 'Friday at 3pm' -> '@fri 3pm', 'next week' -> '@7days', 'push back a week' -> '@14days' if task was already a week out). Use @Xdays, @Yweeks, or @Zmonths where X/Y/Z is the number from today. Add #tags for urgency/priority and +projects as needed."
                            },
                            "notes": {
                                "type": "string",
                                "description": "Task notes/description"
                            },
                            "project_id": {
                                "type": "string",
                                "description": "Project ID to assign task to"
                            },
                            "parent_id": {
                                "type": "string",
                                "description": "Parent task ID for subtasks"
                            }
                        },
                        "required": ["title"]
                    }
                ),
                types.Tool(
                    name="get_tasks",
                    description="Get all tasks from Super Productivity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_done": {
                                "type": "boolean",
                                "description": "Include completed tasks",
                                "default": True
                            }
                        }
                    }
                ),
                types.Tool(
                    name="get_archived_tasks",
                    description="Get all archived tasks from Super Productivity",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="get_current_context_tasks",
                    description="Get tasks from the current context in Super Productivity",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="add_time_to_task",
                    description="Add time to a task's timeSpent. Accepts time in various formats: '30m', '2h', '1.5h', or milliseconds",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to add time to"
                            },
                            "time": {
                                "type": ["integer", "string"],
                                "description": "Time to add. Can be milliseconds (integer) or string like '30m', '2h', '1.5h'"
                            }
                        },
                        "required": ["task_id", "time"]
                    }
                ),
                types.Tool(
                    name="set_time_estimate",
                    description="Set time estimate for a task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to set estimate for"
                            },
                            "time_ms": {
                                "type": "integer",
                                "description": "Time estimate in milliseconds"
                            }
                        },
                        "required": ["task_id", "time_ms"]
                    }
                ),
                types.Tool(
                    name="move_task_to_project",
                    description="Move a task to a different project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to move"
                            },
                            "project_id": {
                                "type": "string",
                                "description": "Target project ID"
                            }
                        },
                        "required": ["task_id", "project_id"]
                    }
                ),
                types.Tool(
                    name="add_tag_to_task",
                    description="Add a tag to a task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to add tag to"
                            },
                            "tag_id": {
                                "type": "string",
                                "description": "Tag ID to add"
                            }
                        },
                        "required": ["task_id", "tag_id"]
                    }
                ),
                types.Tool(
                    name="remove_tag_from_task",
                    description="Remove a tag from a task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to remove tag from"
                            },
                            "tag_id": {
                                "type": "string",
                                "description": "Tag ID to remove"
                            }
                        },
                        "required": ["task_id", "tag_id"]
                    }
                ),
                types.Tool(
                    name="update_task",
                    description="Update an existing task. When users provide natural language with time/date references, convert them to Super Productivity syntax in the title field.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title with Super Productivity syntax. Convert natural language time/date references to @syntax using days/weeks/months from TODAY (e.g., 'push back a week' -> '@14days' if task was already a week out, 'move to next Friday' -> '@5days' if next Friday is 5 days from today, 'reschedule for tomorrow' -> '@1days'). Use @Xdays, @Yweeks, or @Zmonths where X/Y/Z is the number from today. Add #tags for urgency/priority and +projects as needed."
                            },
                            "notes": {
                                "type": "string",
                                "description": "New task notes"
                            },
                            "is_done": {
                                "type": "boolean",
                                "description": "Mark task as done/undone"
                            },
                            "time_estimate": {
                                "type": "integer",
                                "description": "Time estimate in milliseconds"
                            },
                            "time_spent": {
                                "type": "integer",
                                "description": "Time spent in milliseconds"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                types.Tool(
                    name="complete_and_archive_task",
                    description="Complete a task (mark as done) in Super Productivity - NOTE: True deletion is not supported",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to complete"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                types.Tool(
                    name="get_projects",
                    description="Get all projects from Super Productivity",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="create_project",
                    description="Create a new project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Project title"
                            },
                            "description": {
                                "type": "string",
                                "description": "Project description"
                            },
                            "color": {
                                "type": "string",
                                "description": "Project color (hex code)"
                            }
                        },
                        "required": ["title"]
                    }
                ),
                types.Tool(
                    name="update_project",
                    description="Update an existing project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Project ID to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New project title"
                            },
                            "description": {
                                "type": "string",
                                "description": "New project description"
                            },
                            "color": {
                                "type": "string",
                                "description": "New project color (hex code)"
                            }
                        },
                        "required": ["project_id"]
                    }
                ),
                types.Tool(
                    name="get_tags",
                    description="Get all tags from Super Productivity",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="create_tag",
                    description="Create a new tag",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Tag title"
                            },
                            "color": {
                                "type": "string",
                                "description": "Tag color (hex code)"
                            }
                        },
                        "required": ["title"]
                    }
                ),
                types.Tool(
                    name="update_tag",
                    description="Update an existing tag",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tag_id": {
                                "type": "string",
                                "description": "Tag ID to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New tag title"
                            },
                            "color": {
                                "type": "string",
                                "description": "New tag color (hex code)"
                            }
                        },
                        "required": ["tag_id"]
                    }
                ),
                types.Tool(
                    name="show_notification",
                    description="Show a notification in Super Productivity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Notification message"
                            },
                            "type": {
                                "type": "string",
                                "enum": ["success", "info", "warning", "error"],
                                "description": "Notification type",
                                "default": "info"
                            }
                        },
                        "required": ["message"]
                    }
                ),
                types.Tool(
                    name="reorder_tasks",
                    description="Reorder tasks in a context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Array of task IDs in new order"
                            },
                            "context_id": {
                                "type": "string",
                                "description": "Context ID (optional)"
                            },
                            "context_type": {
                                "type": "string",
                                "description": "Context type (optional)"
                            }
                        },
                        "required": ["task_ids"]
                    }
                ),
                types.Tool(
                    name="batch_operation",
                    description="Execute multiple operations in sequence",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "action": {"type": "string"},
                                        "data": {"type": "object"},
                                        "taskId": {"type": "string"},
                                        "projectId": {"type": "string"},
                                        "tagId": {"type": "string"}
                                    },
                                    "required": ["action"]
                                },
                                "description": "List of operations to execute"
                            }
                        },
                        "required": ["operations"]
                    }
                ),
                types.Tool(
                    name="debug_directories",
                    description="Debug the communication directories and show their status",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[types.TextContent]:
            """Handle tool calls"""
            try:
                if name == "create_task":
                    result = await self.create_task(arguments)
                elif name == "get_tasks":
                    result = await self.get_tasks(arguments)
                elif name == "get_archived_tasks":
                    result = await self.get_archived_tasks(arguments)
                elif name == "get_current_context_tasks":
                    result = await self.get_current_context_tasks(arguments)
                elif name == "add_time_to_task":
                    result = await self.add_time_to_task(arguments)
                elif name == "set_time_estimate":
                    result = await self.set_time_estimate(arguments)
                elif name == "move_task_to_project":
                    result = await self.move_task_to_project(arguments)
                elif name == "add_tag_to_task":
                    result = await self.add_tag_to_task(arguments)
                elif name == "remove_tag_from_task":
                    result = await self.remove_tag_from_task(arguments)
                elif name == "update_project":
                    result = await self.update_project(arguments)
                elif name == "update_tag":
                    result = await self.update_tag(arguments)
                elif name == "update_task":
                    result = await self.update_task(arguments)
                elif name == "complete_and_archive_task":
                    result = await self.complete_and_archive_task(arguments)
                elif name == "get_projects":
                    result = await self.get_projects(arguments)
                elif name == "create_project":
                    result = await self.create_project(arguments)
                elif name == "get_tags":
                    result = await self.get_tags(arguments)
                elif name == "create_tag":
                    result = await self.create_tag(arguments)
                elif name == "show_notification":
                    result = await self.show_notification(arguments)
                elif name == "reorder_tasks":
                    result = await self.reorder_tasks(arguments)
                elif name == "batch_operation":
                    result = await self.batch_operation(arguments)
                elif name == "debug_directories":
                    result = await self.debug_directories(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

                return [types.TextContent(type="text", text=str(result))]

            except Exception as e:
                logging.error(f"Error in tool {name}: {str(e)}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def send_command(self, action: str, **kwargs) -> Dict[str, Any]:
        """Send a command to Super Productivity plugin"""
        command = {
            "action": action,
            "id": f"{action}_{asyncio.get_event_loop().time()}",
            "timestamp": asyncio.get_event_loop().time(),
            **kwargs
        }

        # Write command file
        command_file = self.command_dir / f"{command['id']}.json"
        with open(command_file, 'w') as f:
            json.dump(command, f, indent=2)

        logging.info(f"Sent command: {action} -> {command_file}")

        # Wait for response (with timeout)
        response_file = self.response_dir / f"{command['id']}_response.json"

        for _ in range(30):  # Wait up to 30 seconds
            if response_file.exists():
                try:
                    with open(response_file, 'r') as f:
                        response = json.load(f)

                    # Clean up response file
                    response_file.unlink()

                    logging.info(f"Received response for {action}: {response.get('success', 'unknown')}")
                    return response

                except Exception as e:
                    logging.error(f"Error reading response file: {e}")
                    break

            await asyncio.sleep(1)

        # Timeout
        logging.warning(f"Timeout waiting for response to {action}")
        return {"success": False, "error": "Timeout waiting for response"}

    def parse_task_syntax(self, title: str) -> tuple:
        """Parse Super Productivity task syntax from title"""
        title_clean = title

        # Extract tags from title (format: #tagname)
        tag_matches = re.findall(r'#(\w+)', title_clean)
        title_clean = re.sub(r'\s*#\w+', '', title_clean).strip()

        # Extract projects from title (format: +projectname)
        project_matches = re.findall(r'\+(\w+)', title_clean)
        title_clean = re.sub(r'\s*\+\w+', '', title_clean).strip()

        # Extract scheduling syntax (format: @fri 4pm, @tomorrow, @2024-01-15, etc.)
        schedule_matches = re.findall(r'@(\w+(?:\s+\d+[ap]m)?)', title_clean, re.IGNORECASE)
        title_clean = re.sub(r'\s*@\w+(?:\s+\d+[ap]m)?', '', title_clean, flags=re.IGNORECASE).strip()

        # Extract time estimate/spent syntax (format: 10m/3h, 2h, 30m, etc.)
        time_matches = re.findall(r'(\d+[mh](?:/\d+[mh])?)', title_clean)
        title_clean = re.sub(r'\s*\d+[mh](?:/\d+[mh])?', '', title_clean).strip()

        return title_clean, tag_matches, project_matches, schedule_matches, time_matches

    def convert_time_to_ms(self, time_input) -> int:
        """Convert time string like '30m', '2h', '1.5h' to milliseconds"""
        if isinstance(time_input, int):
            return time_input  # Already in ms

        time_str = str(time_input).lower().strip()

        if time_str.endswith('ms'):
            return int(float(time_str[:-2]))
        elif time_str.endswith('s'):
            return int(float(time_str[:-1]) * 1000)
        elif time_str.endswith('m'):
            return int(float(time_str[:-1]) * 60 * 1000)
        elif time_str.endswith('h'):
            return int(float(time_str[:-1]) * 60 * 60 * 1000)
        else:
            # Assume minutes if no unit
            try:
                return int(float(time_str) * 60 * 1000)
            except ValueError:
                return 0

    async def create_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        title = args.get("title", "")

        # Create the task data - Claude should have already converted natural language to SP syntax
        task_data = {
            "title": title,  # Use title as provided by Claude (should already have @syntax)
            "notes": args.get("notes", ""),
            "timeEstimate": args.get("time_estimate", 0),
            "projectId": args.get("project_id"),
            "parentId": args.get("parent_id"),
            "tagIds": []
        }

        return await self.send_command("addTask", data=task_data)

    async def get_tasks(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get all tasks"""
        return await self.send_command("getTasks")

    async def get_archived_tasks(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get all archived tasks"""
        return await self.send_command("getArchivedTasks")

    async def get_current_context_tasks(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get tasks from current context"""
        return await self.send_command("getCurrentContextTasks")

    async def add_time_to_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Add time to a task"""
        task_id = args.get("task_id")
        time_input = args.get("time")
        if not task_id or time_input is None:
            return {"success": False, "error": "task_id and time are required"}

        time_ms = self.convert_time_to_ms(time_input)
        return await self.send_command("addTimeToTask", taskId=task_id, timeMs=time_ms)

    async def set_time_estimate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Set time estimate for a task"""
        task_id = args.get("task_id")
        time_ms = args.get("time_ms")
        if not task_id or time_ms is None:
            return {"success": False, "error": "task_id and time_ms are required"}

        return await self.send_command("setTimeEstimate", taskId=task_id, timeMs=time_ms)

    async def move_task_to_project(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Move task to a different project"""
        task_id = args.get("task_id")
        project_id = args.get("project_id")
        if not task_id or not project_id:
            return {"success": False, "error": "task_id and project_id are required"}

        return await self.send_command("moveTaskToProject", taskId=task_id, projectId=project_id)

    async def add_tag_to_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Add tag to a task"""
        task_id = args.get("task_id")
        tag_id = args.get("tag_id")
        if not task_id or not tag_id:
            return {"success": False, "error": "task_id and tag_id are required"}

        return await self.send_command("addTagToTask", taskId=task_id, tagId=tag_id)

    async def remove_tag_from_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Remove tag from a task"""
        task_id = args.get("task_id")
        tag_id = args.get("tag_id")
        if not task_id or not tag_id:
            return {"success": False, "error": "task_id and tag_id are required"}

        return await self.send_command("removeTagFromTask", taskId=task_id, tagId=tag_id)

    async def update_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task"""
        task_id = args.get("task_id")
        if not task_id:
            return {"success": False, "error": "task_id is required"}

        updates = {}

        # Handle title - Claude should have already converted natural language to SP syntax
        if "title" in args:
            updates["title"] = args["title"]

        if "notes" in args:
            updates["notes"] = args["notes"]
        if "is_done" in args:
            updates["isDone"] = args["is_done"]
            if args["is_done"]:
                updates["doneOn"] = asyncio.get_event_loop().time() * 1000
            else:
                updates["doneOn"] = None
        if "time_estimate" in args:
            updates["timeEstimate"] = args["time_estimate"]
        if "time_spent" in args:
            updates["timeSpent"] = args["time_spent"]

        return await self.send_command("updateTask", taskId=task_id, data=updates)

    async def complete_and_archive_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Complete a task (mark as done) - true deletion is not supported"""
        task_id = args.get("task_id")
        if not task_id:
            return {"success": False, "error": "task_id is required"}

        # Mark task as done instead of deleting
        return await self.send_command("setTaskDone", taskId=task_id)

    async def get_projects(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get all projects"""
        return await self.send_command("getAllProjects")

    async def create_project(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project"""
        project_data = {
            "title": args.get("title", ""),
            "description": args.get("description", ""),
            "color": args.get("color", "#2196F3")
        }

        return await self.send_command("addProject", data=project_data)

    async def update_project(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing project"""
        project_id = args.get("project_id")
        if not project_id:
            return {"success": False, "error": "project_id is required"}

        updates = {}
        if "title" in args:
            updates["title"] = args["title"]
        if "description" in args:
            updates["description"] = args["description"]
        if "color" in args:
            updates["color"] = args["color"]

        return await self.send_command("updateProject", projectId=project_id, data=updates)

    async def get_tags(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get all tags"""
        return await self.send_command("getAllTags")

    async def create_tag(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tag"""
        tag_data = {
            "title": args.get("title", ""),
            "color": args.get("color", "#FF9800")
        }

        return await self.send_command("addTag", data=tag_data)

    async def update_tag(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing tag"""
        tag_id = args.get("tag_id")
        if not tag_id:
            return {"success": False, "error": "tag_id is required"}

        updates = {}
        if "title" in args:
            updates["title"] = args["title"]
        if "color" in args:
            updates["color"] = args["color"]

        return await self.send_command("updateTag", tagId=tag_id, data=updates)

    async def show_notification(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Show a notification"""
        return await self.send_command("showSnack", message=args.get("message", ""))

    async def reorder_tasks(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Reorder tasks in a context"""
        task_ids = args.get("task_ids")
        if not task_ids or not isinstance(task_ids, list):
            return {"success": False, "error": "task_ids array is required"}

        context_id = args.get("context_id")
        context_type = args.get("context_type")

        return await self.send_command("reorderTasks", taskIds=task_ids, contextId=context_id, contextType=context_type)

    async def batch_operation(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multiple operations in sequence"""
        operations = args.get("operations")
        if not operations or not isinstance(operations, list):
            return {"success": False, "error": "operations array is required"}

        return await self.send_command("batchOperation", operations=operations)

    async def debug_directories(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "base_directory": str(self.base_dir),
            "command_directory": str(self.command_dir),
            "response_directory": str(self.response_dir),
            "directories_exist": {
                "base": self.base_dir.exists(),
                "commands": self.command_dir.exists(),
                "responses": self.response_dir.exists()
            }
        }

    async def run(self):
        """Run the MCP server"""
        print("Starting Super Productivity MCP Server...", file=sys.stderr)
        logging.info("Starting Super Productivity MCP Server...")

        # Initialize server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="super-productivity",
                    server_version="1.0.1",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


async def main():
    """Main entry point"""
    server = SuperProductivityMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
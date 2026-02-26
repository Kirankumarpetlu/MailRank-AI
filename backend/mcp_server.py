import asyncio
import inspect
from typing import Any, Callable


class MCPServer:
    """
    Model Context Protocol (MCP) Server.

    Provides a tool registry that agents can use to discover and execute tools
    through a unified interface instead of direct function calls.
    """

    def __init__(self):
        self.tools: dict[str, dict[str, Any]] = {}

    def register_tool(self, name: str, func: Callable, description: str = "") -> None:
        """Register a tool function with the server."""
        self.tools[name] = {
            "function": func,
            "description": description or func.__doc__ or "",
            "name": name,
        }

    def list_tools(self) -> list[dict[str, str]]:
        """List all registered tools with their descriptions."""
        return [
            {"name": info["name"], "description": info["description"]}
            for info in self.tools.values()
        ]

    async def execute_tool(self, name: str, input_data: dict = None) -> dict:
        """
        Execute a registered tool by name.

        Args:
            name: The registered tool name.
            input_data: Keyword arguments to pass to the tool function.

        Returns:
            Dict with 'success' and 'result' or 'error' keys.
        """
        if name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{name}' not found. Available: {list(self.tools.keys())}",
            }

        func = self.tools[name]["function"]
        input_data = input_data or {}

        try:
            # Support both sync and async tool functions
            if inspect.iscoroutinefunction(func):
                result = await func(**input_data)
            else:
                result = await asyncio.to_thread(func, **input_data)

            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

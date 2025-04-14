from mcp import start_server
from mcp.tools import CommandTool, add_builtin_tools
from mcp.runtime import ToolContext

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

# Create tool context
context = ToolContext()

# Register built-in command line tools
add_builtin_tools(context)

# Register custom addition tool
context.register_tool(
    name="add_numbers",
    description="Add two integers",
    func=add_numbers,
    param_schema={
        "type": "object",
        "properties": {
            "a": {"type": "integer"},
            "b": {"type": "integer"}
        },
        "required": ["a", "b"]
    }
)

# Start the server
if __name__ == "__main__":
    start_server(context, port=5050, enable_cors=True)

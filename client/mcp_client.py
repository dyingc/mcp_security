from mcp.client import MCPClient
from langgraph.prebuilt import ToolExecutor

class MCPDemoClient:
    def __init__(self, server_url="http://localhost:5050"):
        self.client = MCPClient(server_url)
        self.tool_executor = ToolExecutor(self.client.get_tools())
    
    def execute_remote_tool(self, tool_name: str, params: dict):
        """Execute remote tool"""
        return self.tool_executor.execute(tool_name, params)
    
    def get_available_tools(self):
        """Get available tools list"""
        return self.client.list_tools()

if __name__ == "__main__":
    # Initialize client
    client = MCPDemoClient()
    
    # Example usage
    print("Available Tools:", client.get_available_tools())
    
    # Execute addition tool
    result = client.execute_remote_tool("add_numbers", {"a": 5, "b": 3})
    print("Result of adding:", result)
    
    # Example command execution
    # cmd_result = client.execute_remote_tool("execute_command", {"command": "ls -l"})
    # print("Command execution result:", cmd_result)

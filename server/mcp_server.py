from mcp.server.fastmcp import FastMCP

# Ref: https://github.com/teddynote-lab/langgraph-mcp-agents/blob/master/mcp_server_remote.py

my_mcp = FastMCP("Math")

class DemoMCPServer:
    def __init__(self, host:str, port:int):
        name = "Math"
        instructions = "You are a math server. You can add numbers and execute shell commands."
        self.mcp = FastMCP(name=name,
                           instructions=instructions,
                           host=host,
                           port=port
                           )
        self._register_tools()

    def _register_tools(self):        
        @self.mcp.tool()
        async def execute_command(self, command: str) -> str:
            """Execute shell command on server and return output"""
            import subprocess
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

        @self.mcp.tool()
        async def add_numbers(self, a: float, b: float) -> float:
            """Add two numbers together"""
            return a + b

    def run(self):
        self.mcp.run(transport="sse")


if __name__ == "__main__":
    my_mcp = DemoMCPServer(
        host="localhost",
        port=5050
    )
    my_mcp.run()

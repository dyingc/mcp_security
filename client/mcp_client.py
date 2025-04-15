import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import AnyMessage
from typing import List

# Ensure project root is in path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from client.utils import (
    get_llm,
    get_mcp_client_config,
    output_responses,
    output_tools,
)

class DemoMCPClient:
    def __init__(self, llm_name:str, config_file:str):
        self.mcp_config = get_mcp_client_config(config_file)
        self.llm = get_llm(llm_name, config_file)

    async def run(self, query: str)->List[AnyMessage]:
        async with MultiServerMCPClient(self.mcp_config) as mcp_client:
            tools = mcp_client.get_tools()
            output_tools(tools)
            self.agent = create_react_agent(self.llm, tools)
            response = await self.agent.ainvoke({"messages": [query]})
        return response.get("messages", [])


async def main():
    load_dotenv()
    config_file = "client/client_config.yaml"
    llm_name = "my_demo_mcp_client"
    demo_client = DemoMCPClient(llm_name, config_file)
    query = "What is the result of 2 + 2?"
    response_messages = await demo_client.run(query)
    output_responses(response_messages)

if __name__ == "__main__":
    asyncio.run(main())
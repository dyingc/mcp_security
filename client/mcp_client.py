from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import yaml
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
import asyncio

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
    
class DemoMCPClient:
    def __init__(self, llm, agent, mcp_client):
        self.llm = llm
        self.agent = agent
        self.mcp_client = mcp_client

    @classmethod
    async def create(cls):
        # Load environment variables
        load_dotenv()

        # Create an instance to access non-async methods
        temp = cls.__new__(cls)
        llm = temp.get_llm("MCP_Client")
        mcp_client = await temp._get_mcp_client("my_demo_mcp_client")
        agent = create_react_agent(llm, mcp_client.get_tools())

        return cls(llm=llm, agent=agent, mcp_client=mcp_client)

    def get_config(self, config_file: str = "client/client_config.yaml"):
        """Load configuration from a YAML file"""
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)
        return config

    def get_llm(self, llm_name: str):
        config = self.get_config()
        model_name = config.get("agent_config").get("model_name")
        temperature = config.get("agent_config").get("temperature", 0.0)
        api_key = os.getenv("DEEPSEEK_API_KEY")  # fixed typo: os.gentenv -> os.getenv
        llm = ChatDeepSeek(model_name=model_name, api_key=api_key, temperature=temperature)
        llm.name = llm_name
        return llm

    async def get_agent(self):
        if not self.agent:
            raise ValueError("Agent is not initialized. Call create() first.")
        return self.agent

    async def _get_mcp_client(self, name: str) -> MultiServerMCPClient:
        config = self.get_config()
        server = config.get("mcp_server").get("server", "localhost")
        server_port = config.get("mcp_server").get("server_port", 5050)
        mcp_protocol = config.get("mcp_server").get("mcp_protocol", "sse")
        server_url = f"http://{server}:{server_port}/{mcp_protocol}"
        client_config_dict = {
            "my_demo_mcp_client": {
                "url": server_url,
                "transport": mcp_protocol,
            }
        }
        self._client_instance = MultiServerMCPClient(client_config_dict)
        # Explicitly initialize connection (this part is necessary)
        await self._client_instance.__aenter__()
        print(self._client_instance.get_tools())
        return self._client_instance

    async def run(self, input_text: str):
        result = await self.agent.ainvoke(input={"messages": [input_text]})
        print(result)

async def main():
    client = await DemoMCPClient.create()
    await client.run("What is 2 + 2?")

if __name__ == "__main__":
    asyncio.run(main())
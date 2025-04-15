import asyncio
import os
import sys
import yaml
from pathlib import Path
from dotenv import load_dotenv

from langchain_deepseek import ChatDeepSeek
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

# Ensure project root is in path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))


class DemoMCPClient:
    def __init__(self, llm, agent):
        self.llm = llm
        self.agent = agent

    @staticmethod
    def get_config(config_file: str = "client/client_config.yaml"):
        with open(config_file, "r") as file:
            return yaml.safe_load(file)

    @staticmethod
    def get_llm(config: dict, llm_name: str):
        model_name = config["agent_config"]["model_name"]
        temperature = config["agent_config"].get("temperature", 0.0)
        api_key = os.getenv("DEEPSEEK_API_KEY")
        llm = ChatDeepSeek(model_name=model_name, api_key=api_key, temperature=temperature)
        llm.name = llm_name
        return llm

    @staticmethod
    def get_mcp_client_config(config: dict):
        server = config["mcp_server"].get("server", "localhost")
        server_port = config["mcp_server"].get("server_port", 5050)
        mcp_protocol = config["mcp_server"].get("mcp_protocol", "sse")
        server_url = f"http://{server}:{server_port}/{mcp_protocol}"
        return {
            "my_demo_mcp_client": {
                "url": server_url,
                "transport": mcp_protocol,
            }
        }

    async def run(self, input_text: str):
        response = await self.agent.ainvoke({"messages": [input_text]})
        return response


async def main():
    load_dotenv()
    config = DemoMCPClient.get_config()
    mcp_config_dict = DemoMCPClient.get_mcp_client_config(config)

    # Clean resource management with async context
    async with MultiServerMCPClient(mcp_config_dict) as mcp_client:
        print("[MCP Client Tools]:\n" + "\n".join([f"Tool {i:02d}:\n" + str(tool) for i, tool in enumerate(mcp_client.get_tools())]))

        llm = DemoMCPClient.get_llm(config, llm_name="MCP_Client")
        agent = create_react_agent(llm, mcp_client.get_tools())

        # You now have `agent` right here and can use it directly
        client = DemoMCPClient(llm, agent)
        result_chain = await client.run("Can you calculate the sum of FOUR and 8.5 and tell me the answer?")
        print("\n[Result Chain]:\n" + "\n".join([f"Message {i:02d}:\n{str(message)}" for i, message in enumerate(result_chain.get('messages', []))]))

if __name__ == "__main__":
    asyncio.run(main())
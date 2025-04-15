from langchain_deepseek import ChatDeepSeek
import yaml
import os
from langchain_core.language_models.chat_models import BaseChatModel
from typing import Dict, Any

def get_llm(llm_name: str, config_file:str="client/client_config.yaml")->BaseChatModel:
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    model_name = config["agent_config"]["model_name"]
    temperature = config["agent_config"].get("temperature", 0.0)
    api_key = os.getenv("DEEPSEEK_API_KEY")
    llm = ChatDeepSeek(model_name=model_name, api_key=api_key, temperature=temperature)
    llm.name = llm_name
    return llm

def get_mcp_client_config(config_file:str="client/client_config.yaml") -> Dict[str, Dict[str, str]]:
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
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

def get_config(config_file: str = "client/client_config.yaml"):
    with open(config_file, "r") as file:
        return yaml.safe_load(file)


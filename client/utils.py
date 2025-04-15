from langchain_deepseek import ChatDeepSeek
import yaml
import os
from langchain_core.language_models.chat_models import BaseChatModel
from typing import Dict, Any, List
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
)
from langchain_core.tools.structured import StructuredTool

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

def output_responses(messages: List[AnyMessage]):
    """
    Prints out the content of each message in the given list.

    Args:
    messages (List[Message]): A list of messages where each message is an instance of either AIMessage, HumanMessage, or another type.
    """
    for msg in messages:
        if isinstance(msg, AIMessage):
            if msg.content:
                print(f"\nAI: {msg.content}")
            if msg.tool_calls:
                print("\nAI calls tools:")
                tool_calls = msg.tool_calls
                for t in tool_calls:
                    func_name = t.get('name', None)
                    args = t.get('args', [])
                    if func_name:
                        args_repr = ", ".join([f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}" for k, v in args.items()])
                        func_call_repr = f"- Function call: {func_name}({args_repr})"
                        print(func_call_repr)
        elif isinstance(msg, HumanMessage):
            print(f"\nUser: {msg.content}")
        elif isinstance(msg, ToolMessage):
            print(f"\nTool execution result: {msg.content}")
        else:
            print("\n" + msg.content)
    print("\n")

def output_tools(tools: List[StructuredTool]):
    """
    Prints out the name and description, as well as the info of arguments, of each tool in the given list.

    Args:
    tools (List[StructuredTool]): A list of tools where each tool is an instance of StructuredTool.
    """
    for i, tool in enumerate(tools):
        tool_name = tool.name
        tool_desc = tool.description
        tool_desc = [f"\t\t{line}" if line else "" for line in f"{tool_desc}".split('\n')]
        tool_desc = "\n".join(tool_desc)
        tool_args = tool.args_schema
        print(f"Tool {i+1:d}:")
        print(f"\tName: {tool_name}")
        print(f"\tDescription:\n{tool_desc}")
        print(f"\tArgs:")
        properties = tool_args.get("properties", {})
        required = tool_args.get("required", [])
        for prop, schema in properties.items():
            if prop in required:
                print(f"\t\t{prop} (required): {schema}")
            else:
                print(f"\t\t{prop} (optional): {schema}")
        print("\n")
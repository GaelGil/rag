from app.chat.agent.utils.OpenAIClient import OpenAIClient
from app.chat.agent.utils.PlannerAgent import PlannerAgent
from app.chat.agent.utils.Executor import Executor
from app.chat.agent.MCP.client import MCPClient
from app.chat.agent.utils.schemas import Plan
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path("../../.env"))

class ChatServices:
    def __init__(self):
        pass    

    def init_chat_services(self):
        pass

    def process_message(self, message):
        pass
    
    def extract_tools(self, tool_call):
        pass

    def call_tools(self, tool_calls):
        pass

    def stream_response(self, message):
        pass
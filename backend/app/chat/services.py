from app.chat.agent.utils.OpenAIClient import OpenAIClient
from app.chat.agent.utils.PlannerAgent import PlannerAgent
from app.chat.agent.utils.Executor import Executor
from app.chat.agent.MCP.client import MCPClient
from app.chat.agent.utils.schemas import Plan
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
from composio import Composio  # type: ignore
import os
load_dotenv(Path("../../.env"))

class ChatServices:
    def __init__(self):
        self.chat_history = []
        self.planner: PlannerAgent = None
        self.mcp_client: MCPClient = None
        self.llm: OpenAI = None
        self.tools = None
        self.model_name: str = "gpt-4.1-mini"
        self.composio = Composio()
        self.user_id = "0000-1111-2222"
        self.previous_task_results: list[dict] = [
            {
                "task_id": "0",
                "task": "first task, no previous task yet",
                "results": "first task, no results yet",
            }
        ]
        pass    

    def init_chat_services(self):
        print("Initializing OpenAI client ...")
        self.llm = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY")).get_client()

        print("Initializing Planner Agent ...")
        self.planner = PlannerAgent(
            dev_prompt="",
            llm=self.llm,
            messages=[],
        )

    def process_message(self, message):
        pass
    
    def extract_tools(self, tool_call):
        pass

    def call_tools(self, tool_calls):
        pass

    def stream_response(self, message):
        pass
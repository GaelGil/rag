from app.chat.agent.utils.OpenAIClient import OpenAIClient
from app.chat.agent.utils.PlannerAgent import PlannerAgent

# from app.chat.agent.utils.Executor import Executor
from app.chat.agent.MCP.client import MCPClient

# from app.chat.agent.utils.schemas import Plan
from app.chat.agent.utils.prompts import CHATBOT_PROMPT
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from composio import Composio  # type: ignore
import os
import json

load_dotenv(Path("../../.env"))


# Example tool function
def get_weather(location: str) -> str:
    # Here you would implement actual weather lookup logic
    return f"The current temperature in {location} is 72°F."


# Define your tools schema like your snippet
tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current temperature for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and country e.g. Bogotá, Colombia",
                }
            },
            "required": ["location"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


class ChatService:
    def __init__(self):
        self.chat_history: list[dict]
        self.planner: PlannerAgent = None
        self.mcp_client: MCPClient = None
        self.llm: OpenAI = None
        self.tools = tools
        self.tool_functions = {"get_weather": get_weather}
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
            dev_prompt=CHATBOT_PROMPT,
            llm=self.llm,
            messages=[],
        )

    def add_chat_history(self, role: str, message: str):
        self.chat_history.append({"role": role, "content": message})

    async def process_message(self, message):
        self.add_chat_history(role="user", message=message)
        stream = self.llm.responses.create(
            model=self.model_name, input=self.chat_history, stream=True
        )

        assistant_text = ""
        tool_call = None

        # Stream tokens from initial response
        async for event in stream:
            delta = event.choices[0].delta
            tool_call = delta.get("tool_call")

            if tool_call and isinstance(tool_call, dict):
                tool_name = tool_call.get("name")
                tool_args_str = tool_call.get("arguments")

                if not tool_name or not tool_args_str:
                    # Invalid tool_call, ignore and continue streaming text
                    tool_call = None
                else:
                    # Yield user-friendly message about tool call
                    msg = f"\n[Calling tool {tool_name} with args {tool_args_str}]...\n"
                    yield msg
                    break  # Exit streaming to handle the tool call

            if not tool_call:
                content = delta.get("content", "")
                assistant_text += content
                yield content

        # Handle tool call if detected
        if tool_call:
            try:
                tool_args = json.loads(tool_args_str)
            except (json.JSONDecodeError, TypeError):
                tool_args = {}

            tool_function = self.tool_functions.get(tool_name)
            if not tool_function:
                tool_result = f"[Error] Tool '{tool_name}' not implemented."
            else:
                try:
                    tool_result = tool_function(**tool_args)
                except Exception as e:
                    tool_result = f"[Error] Exception calling tool '{tool_name}': {e}"

            # Add tool result to system messages in history
            self.add_chat_history("system", f"Tool {tool_name} returned: {tool_result}")

            # Resume conversation with tool info in history
            stream2 = self.client.responses.create(
                model="gpt-5",
                input=self.chat_history,
                tools=self.tools,
                stream=True,
            )

            assistant_text = ""
            async for event in stream2:
                delta = event.choices[0].delta
                content = delta.get("content", "")
                assistant_text += content
                yield content

            # Append final assistant response to history
            self.add_chat_history("assistant", assistant_text)

        else:
            # No tool call, append assistant text to history
            self.add_chat_history("assistant", assistant_text)

    def extract_tools(self, tool_call):
        pass

    def call_tools(self, tool_calls):
        pass

    def stream_response(self, message):
        pass

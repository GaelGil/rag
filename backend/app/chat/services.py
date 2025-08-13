from app.chat.agent.utils.OpenAIClient import OpenAIClient
from app.chat.agent.utils.PlannerAgent import PlannerAgent
from app.chat.agent.MCP.client import MCPClient
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
        self.chat_history: list[dict] = []
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
        self.add_chat_history(role="developer", message=CHATBOT_PROMPT)

    def add_chat_history(self, role: str, message: str):
        self.chat_history.append({"role": role, "content": message})

    def call_function(self, name, args):
        if name == "get_weather":
            res = get_weather(args["location"])
            return res

    def process_message(self, message):
        self.add_chat_history(role="user", message=message)
        print(f"process_message called with message: {message}")  # DEBUG

        stream = self.llm.responses.create(
            model=self.model_name,
            input=self.chat_history,
            tools=self.tools,
            tool_choice="auto",
            stream=True,
        )

        assistant_text = ""
        tool_call = None

        print("Starting LLM stream")
        for event in stream:
            print(f"Received event: {event}")

            if hasattr(event, "delta"):
                delta_content = event.delta
                if isinstance(delta_content, str):
                    content = delta_content
                elif isinstance(delta_content, dict):
                    # If dict, extract 'content' field safely
                    content = delta_content.get("content", "")
                else:
                    content = ""

                assistant_text += content
                yield content
                continue

            for tool_call in event.output:
                if tool_call.type != "function_call":
                    continue
                # select tool name
                tool_name = tool_call.name
                # get the arguments for the tool
                tool_args = json.loads(tool_call.arguments)

                # call the function
                if tool_name == "get_weather":
                    # call the function
                    result = self.call_function(tool_name, tool_args)

                    # Add tool result to chat history
                    self.add_chat_history(
                        role="system",
                        message=f"Tool {tool_name} returned: {result}",
                    )

                    stream2 = self.llm.responses.stream(
                        model=self.model_name,
                        input=self.chat_history,
                    )

                    assistant_text = ""
                    for event in stream2:
                        print(f"Received event: {event}")

                        # Check if event has a direct 'delta' attribute (like ResponseTextDeltaEvent)
                        if hasattr(event, "delta"):
                            # 'delta' could be a string chunk or dict; handle both
                            delta_content = event.delta
                            if isinstance(delta_content, str):
                                content = delta_content
                            elif isinstance(delta_content, dict):
                                # If dict, extract 'content' field safely
                                content = delta_content.get("content", "")
                            else:
                                content = ""

                            assistant_text += content
                            yield content
                            continue

                    self.add_chat_history("assistant", assistant_text)

                    return

            else:
                continue

        print(self.chat_history)

        # If no tool call, add full assistant response after stream ends
        if not tool_call:
            self.add_chat_history("assistant", assistant_text)

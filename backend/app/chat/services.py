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
import logging

# Configure basic logging (e.g., to console)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Get a logger instance
logger = logging.getLogger(__name__)

load_dotenv(Path("../../.env"))


# Example tool function
def get_weather(location: str) -> str:
    # Here you would implement actual weather lookup logic
    return f"The current temperature in {location} is 72°F."


TOOL_HANDLERS = {
    "get_weather": get_weather,
}


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
        """
        Initialize the chat services
        Args:
            None
        Returns:
            None
        """
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
        """Adds a message to the chat history

        Args:
            role (str): The role of the message sender
            message (str): The message content
        Returns:
            None
        """
        self.chat_history.append({"role": role, "content": message})

    def process_message(self, message):
        self.add_chat_history(role="user", message=message)
        logger.info(f"process_message called with message: {message}")

        stream = self.llm.responses.create(
            model=self.model_name,
            input=self.chat_history,
            tools=self.tools,
            tool_choice="auto",
            stream=True,
        )

        tool_calls = {}

        # First pass: collect text + tool calls
        for event in stream:
            print(
                f"\n[DEBUG EVENT] type={event.type}, idx={getattr(event, 'output_index', None)}, delta={getattr(event, 'delta', None)}"
            )

            # Stream partial text
            if event.type == "response.output_text.delta":
                yield event.delta
                print(event.delta, end="", flush=True)

            elif event.type == "response.output_text.done":
                print()

            # New tool call slot
            elif event.type == "response.output_item.added":
                idx = getattr(event, "output_index", 0)
                tool_calls[idx] = {"name": None, "arguments": "", "done": False}
                print(f"[DEBUG] Added tool call slot idx={idx}")

            # Tool name
            elif event.type in (
                "response.function_call.delta",
                "response.tool_call.delta",
            ):
                idx = getattr(event, "output_index", 0)
                if idx not in tool_calls:
                    tool_calls[idx] = {"name": None, "arguments": "", "done": False}
                delta = getattr(event, "delta", None)
                if isinstance(delta, dict) and "name" in delta:
                    tool_calls[idx]["name"] = delta["name"]
                    print(f"[DEBUG] Tool name for idx={idx}: {delta['name']}")

            # Tool arguments fragment
            elif event.type == "response.function_call_arguments.delta":
                idx = getattr(event, "output_index", 0)
                if idx not in tool_calls:
                    tool_calls[idx] = {"name": None, "arguments": "", "done": False}
                frag = (
                    event.delta
                    if not isinstance(event.delta, dict)
                    else json.dumps(event.delta)
                )
                tool_calls[idx]["arguments"] += frag
                print(f"[DEBUG] Arg fragment for idx={idx}: {frag}")

            # Mark tool done
            elif event.type == "response.function_call_arguments.done":
                idx = getattr(event, "output_index", 0)
                if idx not in tool_calls:
                    tool_calls[idx] = {"name": None, "arguments": "", "done": False}
                tool_calls[idx]["done"] = True
                print(f"[DEBUG] Tool idx={idx} marked done")

        # Second pass: execute all tool calls
        for idx, entry in tool_calls.items():
            tool_name = entry["name"]
            args_str = entry["arguments"]

            if not tool_name:
                if len(self.tools) == 1 and "name" in self.tools[0]:
                    tool_name = self.tools[0]["name"]
                    print(f"[DEBUG] No tool name in stream; fallback to {tool_name}")
                else:
                    print(f"[DEBUG] No tool name for idx={idx}, skipping")
                    continue

            try:
                parsed_args = json.loads(args_str or "{}")
            except json.JSONDecodeError:
                parsed_args = {}
                print(f"[DEBUG] Failed to parse args for idx={idx}, using empty dict")

            print(f"[DEBUG] Executing tool {tool_name} with args: {parsed_args}")

            handler = TOOL_HANDLERS.get(tool_name)
            if not handler:
                print(f"[DEBUG] No handler for {tool_name}, skipping")
                continue

            try:
                result = (
                    handler(**parsed_args)
                    if isinstance(parsed_args, dict)
                    else handler(parsed_args)
                )
            except TypeError:
                result = handler(
                    parsed_args.get("location")
                    if isinstance(parsed_args, dict)
                    else parsed_args
                )

            print(f"[DEBUG] Tool result for idx={idx}: {result}")

            self.chat_history.append(
                {
                    "role": "assistant",
                    "content": f"TOOL_NAME: {tool_name}, RESULT: {result}",
                }
            )

        # Third pass: get final assistant answer
        if tool_calls:
            print("[DEBUG] Calling model for final answer...")
            final_stream = self.llm.responses.create(
                model=self.model_name,
                input=self.chat_history,
                stream=True,
            )

            print("Assistant (final): ", end="", flush=True)
            for ev in final_stream:
                print(
                    f"\n[DEBUG EVENT FINAL] type={ev.type}, delta={getattr(ev, 'delta', None)}"
                )
                if ev.type == "response.output_text.delta":
                    yield ev.delta
                    print(ev.delta, end="", flush=True)
                elif ev.type == "response.output_text.done":
                    print()

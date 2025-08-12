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

    def add_chat_history(self, role: str, message: str):
        self.chat_history.append({"role": role, "content": message})

    def process_message(self, message):
        import json

        self.add_chat_history(role="user", message=message)
        print(f"process_message called with message: {message}")  # DEBUG

        stream = self.llm.responses.create(
            model=self.model_name, input=self.chat_history, stream=True
        )

        assistant_text = ""
        tool_call = None

        print("Starting LLM stream")
        for event in stream:
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

            # Else check if event has choices attribute (older style or tool calls)
            if hasattr(event, "choices") and event.choices:
                delta = event.choices[0].delta
                if not delta:
                    continue

                tool_call = delta.get("tool_call")

                if tool_call and isinstance(tool_call, dict):
                    tool_name = tool_call.get("name")
                    tool_args_str = tool_call.get("arguments")

                    if not tool_name or not tool_args_str:
                        tool_call = None
                    else:
                        # Yield tool call message
                        yield f"\n[Calling tool {tool_name} with args {tool_args_str}]...\n"

                        # Try parsing tool arguments
                        try:
                            tool_args = json.loads(tool_args_str)
                        except (json.JSONDecodeError, TypeError):
                            tool_args = {}

                        # Call the tool function
                        tool_function = self.tool_functions.get(tool_name)
                        if not tool_function:
                            tool_result = f"[Error] Tool '{tool_name}' not implemented."
                        else:
                            try:
                                tool_result = tool_function(**tool_args)
                            except Exception as e:
                                tool_result = (
                                    f"[Error] Exception calling tool '{tool_name}': {e}"
                                )

                        # Add tool result to chat history
                        self.add_chat_history(
                            "system", f"Tool {tool_name} returned: {tool_result}"
                        )

                        # Second streaming loop: continue with updated chat history
                        stream2 = self.llm.responses.stream(
                            model=self.model_name,
                            input=self.chat_history,
                            tools=self.tools,
                        )

                        assistant_text = ""
                        for event2 in stream2:
                            if not hasattr(event2, "choices") or not event2.choices:
                                continue

                            delta2 = event2.choices[0].delta
                            if not delta2:
                                continue

                            content2 = delta2.get("content", "")
                            assistant_text += content2
                            yield content2

                        # Add final assistant message to history
                        self.add_chat_history("assistant", assistant_text)

                        # End generator after finishing second stream
                        return

                if not tool_call:
                    content = delta.get("content", "")
                    assistant_text += content
                    yield content

            else:
                # Unknown event type or no content, just ignore
                continue

        # If no tool call, add full assistant response after stream ends
        if not tool_call:
            self.add_chat_history("assistant", assistant_text)

    def extract_tools(self, tool_call):
        pass

    def call_tools(self, tool_calls):
        pass

    def stream_response(self, message):
        pass

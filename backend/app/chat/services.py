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

    def process_and_execute_tool(self, tool_calls, output_index):
        """
        Called when we have final_tool_calls[output_index]['done'] == True.
        Parses args, runs the tool, appends tool result to chat_history and streams final answer.
        """
        entry = tool_calls.get(output_index)
        if not entry:
            print(f"[DEBUG] No entry found for output_index={output_index}")
            return

        tool_name = entry.get("name")
        args_str = entry.get("arguments", "")
        print(
            f"[DEBUG] Processing tool call at index={output_index}: name={tool_name}, raw_args={args_str}"
        )

        # Fallback to single tool if name wasn't sent
        if not tool_name:
            if len(tools) == 1 and "name" in tools[0]:
                tool_name = tools[0]["name"]
                print(
                    f"[DEBUG] No tool name in stream; falling back to single provided tool: {tool_name}"
                )
            else:
                print(
                    "[DEBUG] No tool name and multiple/no tools available — cannot execute safely."
                )
                return

        try:
            parsed_args = json.loads(args_str or "{}")
        except json.JSONDecodeError:
            parsed_args = {}
            print("[DEBUG] Failed to parse JSON args; using empty dict")

        print(f"[DEBUG] Parsed args for {tool_name}: {parsed_args}")

        handler = TOOL_HANDLERS.get(tool_name)
        if not handler:
            print(f"[DEBUG] No local handler for tool '{tool_name}'")
            return

        # Execute the tool
        try:
            # adapt call depending on expected signature
            tool_result = (
                handler(**parsed_args)
                if isinstance(parsed_args, dict)
                else handler(parsed_args)
            )
        except TypeError:
            # fallback if handler expects single positional arg
            tool_result = handler(
                parsed_args.get("location")
                if isinstance(parsed_args, dict)
                else parsed_args
            )

        print(f"[DEBUG] Tool result: {tool_result}")

        # Append tool output for the model to consume
        self.chat_history.append(
            {
                "role": "assistant",
                "content": f"TOOL_NAME: {tool_name}, RESULT: {tool_result}",
            }
        )

        # Re-call the model to get its final answer (streamed)
        print("[DEBUG] Re-calling model to get final answer after tool execution...")
        final_stream = self.llm.responses.create(
            model=self.model_name, input=self.chat_history, tools=tools, stream=True
        )

        print("Assistant (final): ", end="", flush=True)
        for ev in final_stream:
            print(
                f"\n[DEBUG EVENT FINAL] type={ev.type}, delta={getattr(ev, 'delta', None)}"
            )
            if ev.type == "response.output_text.delta":
                print(ev.delta, end="", flush=True)
            elif ev.type == "response.output_text.done":
                print()  # newline

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

        tool_calls = {}

        for event in stream:
            # show the raw event for debugging
            print(
                f"\n[DEBUG EVENT] type={event.type}, output_index={getattr(event, 'output_index', None)}, delta={getattr(event, 'delta', None)}"
            )

            # Normal text streaming
            if event.type == "response.output_text.delta":
                yield event.delta
                print(event.delta, end="", flush=True)

            elif event.type == "response.output_text.done":
                print()

            # When an output item is added, initialize storage for it
            elif event.type == "response.output_item.added":
                idx = getattr(event, "output_index", 0)
                tool_calls[idx] = {
                    "item": getattr(event, "item", None),
                    "name": None,
                    "arguments": "",
                    "done": False,
                }
                print(
                    f"[DEBUG] output_item.added -> initialized final_tool_calls[{idx}]"
                )
            # Some streams send name under function_call.delta or tool_call.delta
            elif event.type in (
                "response.function_call.delta",
                "response.tool_call.delta",
            ):
                idx = getattr(event, "output_index", 0)
                # ensure slot exists
                if idx not in tool_calls:
                    tool_calls[idx] = {
                        "item": None,
                        "name": None,
                        "arguments": "",
                        "done": False,
                    }
                # sometimes delta is a dict with "name"
                delta = getattr(event, "delta", None)
                if isinstance(delta, dict) and "name" in delta:
                    yield delta["name"]
                    tool_calls[idx]["name"] = delta["name"]
                    print(
                        f"[DEBUG] Captured function/tool name for index={idx}: {delta['name']}"
                    )

            # Arguments come token-by-token as strings
            elif event.type == "response.function_call_arguments.delta":
                idx = getattr(event, "output_index", 0)
                if idx not in tool_calls:
                    tool_calls[idx] = {
                        "item": None,
                        "name": None,
                        "arguments": "",
                        "done": False,
                    }
                # delta may be a string fragment
                frag = (
                    event.delta
                    if not isinstance(event.delta, dict)
                    else json.dumps(event.delta)
                )
                tool_calls[idx]["arguments"] += frag
                print(f"[DEBUG] Appended arg fragment to index={idx}: {frag}")

            elif event.type == "response.function_call_arguments.done":
                idx = getattr(event, "output_index", 0)
                if idx not in tool_calls:
                    tool_calls[idx] = {
                        "item": None,
                        "name": None,
                        "arguments": "",
                        "done": False,
                    }
                tool_calls[idx]["done"] = True
                print(
                    f"[DEBUG] function_call_arguments.done for index={idx}. full_args={tool_calls[idx]['arguments']}"
                )

                if idx:
                    # process this particular tool call immediately
                    # self.process_and_execute_tool(idx)
                    entry = tool_calls.get(idx)
                    if not entry:
                        print(f"[DEBUG] No entry found for output_index={idx}")
                        return

                    tool_name = entry.get("name")
                    args_str = entry.get("arguments", "")
                    print(
                        f"[DEBUG] Processing tool call at index={idx}: name={tool_name}, raw_args={args_str}"
                    )

                    # Fallback to single tool if name wasn't sent
                    if not tool_name:
                        if len(tools) == 1 and "name" in tools[0]:
                            tool_name = tools[0]["name"]
                            print(
                                f"[DEBUG] No tool name in stream; falling back to single provided tool: {tool_name}"
                            )
                        else:
                            print(
                                "[DEBUG] No tool name and multiple/no tools available — cannot execute safely."
                            )
                            return

                    try:
                        parsed_args = json.loads(args_str or "{}")
                    except json.JSONDecodeError:
                        parsed_args = {}
                        print("[DEBUG] Failed to parse JSON args; using empty dict")

                    print(f"[DEBUG] Parsed args for {tool_name}: {parsed_args}")

                    handler = TOOL_HANDLERS.get(tool_name)
                    if not handler:
                        print(f"[DEBUG] No local handler for tool '{tool_name}'")
                        return

                    # Execute the tool
                    try:
                        # adapt call depending on expected signature
                        tool_result = (
                            handler(**parsed_args)
                            if isinstance(parsed_args, dict)
                            else handler(parsed_args)
                        )
                    except TypeError:
                        # fallback if handler expects single positional arg
                        tool_result = handler(
                            parsed_args.get("location")
                            if isinstance(parsed_args, dict)
                            else parsed_args
                        )

                    print(f"[DEBUG] Tool result: {tool_result}")

                    # Append tool output for the model to consume
                    self.chat_history.append(
                        {
                            "role": "assistant",
                            "content": f"TOOL_NAME: {tool_name}, RESULT: {tool_result}",
                        }
                    )

                    # Re-call the model to get its final answer (streamed)
                    print(
                        "[DEBUG] Re-calling model to get final answer after tool execution..."
                    )
                    final_stream = self.llm.responses.create(
                        model=self.model_name,
                        input=self.chat_history,
                        tools=tools,
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

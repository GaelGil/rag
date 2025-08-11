from app.chat.agent.utils.OpenAIClient import OpenAIClient
from app.chat.agent.utils.PlannerAgent import PlannerAgent
from app.chat.agent.utils.Executor import Executor
from app.chat.agent.MCP.client import MCPClient
from app.chat.agent.utils.schemas import Plan
from app.chat.agent.utils.prompts import CHATBOT_PROMPT
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from composio import Composio  # type: ignore
import os

load_dotenv(Path("../../.env"))


class ChatServices:
    def __init__(self):
        self.chat_history: list[dict]
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

        # Stream tokens
        for event in stream:
            delta = event.choices[0].delta

            # Detect if model wants to call a tool
            if "tool_call" in delta:
                tool_call = delta["tool_call"]
                # Yield some text telling user you are calling the tool
                msg = f"\n[Calling tool {tool_call['name']} with args {tool_call['arguments']}]...\n"
                yield msg
                break

            # Otherwise yield normal text delta
            content = delta.get("content", "")
            assistant_text += content
            yield content

        if tool_call:
            tool_name = tool_call["name"]
            tool_args_str = tool_call["arguments"]  # usually JSON string
            import json

            tool_args = json.loads(tool_args_str)

            # Call the actual tool function with parsed args
            tool_result = self.tool_functions[tool_name](**tool_args)

            # Append tool result as system message to history

            self.add_chat_history(
                role="system", message=f"Tool {tool_name} returned: {tool_result}"
            )
            # Now ask model again to generate final response incorporating tool result
            stream2 = self.llm.responses.create(
                model="gpt-4.1-mini",
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

            # Append assistant final reply
            self.add_chat_history(role="assistant", message=assistant_text)
        else:
            # No tool call, append assistant text directly
            self.add_chat_history(role="assistant", message=assistant_text)

    def extract_tools(self, tool_call):
        pass

    def call_tools(self, tool_calls):
        pass

    def stream_response(self, message):
        pass

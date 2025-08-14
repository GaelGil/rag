from app.chat.agent.utils.OpenAIClient import OpenAIClient
from app.chat.agent.utils.composio_tools import composio_tools
from app.chat.agent.utils.prompts import CHATBOT_PROMPT
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from composio import Composio
import os
import json
import logging
import traceback

# logging stuff
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
# load env
load_dotenv(Path("../../.env"))


class ChatService:
    def __init__(self):
        self.chat_history: list[dict] = []
        self.model_name: str = "gpt-4.1-mini"
        self.llm: OpenAI = None
        self.tools = composio_tools
        self.composio = Composio()
        self.user_id = "0000-1111-2222"

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

    def execute_tool(self, tool_name, tool_args):
        """Execute a tool

        Args:
            tool_name (str): The name of the tool to execute
            tool_args (dict): The arguments to pass to the tool

        Returns:
            Any: The result of the tool

        """
        logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
        logger.info(
            f"Tool Name Type {type(tool_name)}, Tool Args Type {type(tool_args)}"
        )
        try:
            print(f"User ID: {self.user_id}")
            composio = Composio()
            result = composio.tools.execute(
                slug=tool_name,
                user_id=self.user_id,
                arguments=tool_args,
            )
            logger.info(f"Raw Composio result: {result}")
            logger.info(f"Composio result type: {type(result)}")
            return result
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logger.info("!!! TOOL EXECUTION EXCEPTION !!!")
            logger.info(f"Error type: {type(e).__name__}")
            logger.info(f"Error message: {str(e)}")
            logger.info(f"Traceback: {traceback.format_exc()}")
            return {"error": error_msg}

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

        # initial call
        for event in stream:
            print(
                f"\n[DEBUG EVENT] type={event.type}, idx={getattr(event, 'output_index', None)}, delta={getattr(event, 'delta', None)}"
            )

            # if there is text, print it
            if event.type == "response.output_text.delta":
                yield json.dumps({"type": "response", "text": event.delta})
                logger.info(f"response.output_text.delta: {event.delta}")
                print(event.delta, end="", flush=True)
            # if there is no text, print a newline
            elif event.type == "response.output_text.done":
                print()

            # else if there is a tool call
            # name of the tool is in response.output.item
            elif event.type == "response.output_item.added":
                # output_index is the index of the tool call
                # because they come in chunks we need to keep track of the index
                idx = getattr(event, "output_index", 0)
                if idx not in tool_calls:
                    # if the index is not in the tool calls dict, add it
                    tool_calls[idx] = {
                        "name": None,
                        "arguments_fragments": [],
                        "arguments": None,
                        "done": False,
                    }
                    logger.info(f"[DEBUG] Added tool call slot idx={idx}")
                tool_calls[idx]["name"] = event.item.name  # get the name of the tool

            # else if there is a tool argument (they come in chunks as strings)
            elif event.type == "response.function_call_arguments.delta":
                # output_index is the index of the tool call
                idx = getattr(event, "output_index", 0)
                if idx not in tool_calls:  # if not in the tool calls dict, add it
                    tool_calls[idx] = {
                        "name": None,
                        "arguments_fragments": [],
                        "arguments": None,
                        "done": False,
                    }
                # delta (arguments) may be a string fragment so we add it
                args_frag = (
                    event.delta
                    if isinstance(event.delta, str)
                    else json.dumps(event.delta)
                )
                # add up the argument strings for the tool call
                tool_calls[idx]["arguments_fragments"].append(args_frag)
                logger.info(f"[DEBUG] Arg fragment for idx={idx}: {args_frag}")

            # else if the tool call is done
            elif event.type == "response.function_call_arguments.done":
                # output_index is the index of the tool call
                idx = getattr(event, "output_index", 0)
                # if the index is not in the tool calls dict, add it
                if idx not in tool_calls:
                    tool_calls[idx] = {
                        "name": None,
                        "arguments_fragments": [],
                        "arguments": None,
                        "done": False,
                    }
                # mark the tool call as done
                tool_calls[idx]["done"] = True
                # join the argument fragments into a single string
                tool_calls[idx]["arguments"] = "".join(
                    tool_calls[idx]["arguments_fragments"]
                ).strip()
                # log statment for tool done
                logger.info(f"[DEBUG] Marked tool idx={idx} done")

        logger.info(f"TOOL CALLS: {tool_calls}")

        # Execute the tool calls
        for tool_idx, tool in tool_calls.items():
            tool_name = tool["name"]
            args_str = tool["arguments"]

            if not tool_name:  # if tool name is None
                print(f"[DEBUG] No tool name for idx={tool_idx}, skipping")
                continue  # continue

            # try to parse the arguments
            try:
                parsed_args = json.loads(args_str)
            except json.JSONDecodeError:
                parsed_args = {}
                logger.info(
                    f"[DEBUG] Failed to parse args for idx={tool_idx}, using empty dict"
                )

            yield json.dumps(
                {"type": "tool_use", "tool_name": tool_name, "tool_input": parsed_args}
            )
            try:
                result = self.execute_tool(tool_name, parsed_args)
            except TypeError:
                result = self.execute_tool(tool_name, parsed_args.get("location"))

            # tool_result_data = {
            #     "type": "tool_result",
            #     "tool_name": tool_name,
            #     "tool_input": parsed_args,
            #     "tool_result": result,
            # }

            yield json.dumps(
                {
                    "type": "tool_result",
                    "tool_name": tool_name,
                    "tool_input": parsed_args,
                    "tool_result": result,
                }
            )
            logger.info(f"[DEBUG] Tool result for idx={tool_idx}: {result}")

            self.chat_history.append(
                {
                    "role": "assistant",
                    "content": f"TOOL_NAME: {tool_name}, RESULT: {result}",
                }
            )

        # Get the final answer
        if tool_calls:  # if we called tools to get updated information
            logger.info("[DEBUG] Calling model for final answer...")
            # Call the model again with the tool call results
            final_stream = self.llm.responses.create(
                model=self.model_name,
                input=self.chat_history,
                stream=True,
            )

            print("Assistant (final): ", end="", flush=True)
            # Stream partial text
            for ev in final_stream:
                logger.info(
                    f"\n[DEBUG EVENT FINAL] type={ev.type}, delta={getattr(ev, 'delta', None)}"
                )
                # if there is text, print it/yield it
                if ev.type == "response.output_text.delta":
                    yield json.dumps({"type": "response", "text": event.delta})
                    logger.info(ev.delta)
                    print(ev.delta, end="", flush=True)
                # if there is no text, print a newline
                elif ev.type == "response.output_text.done":
                    print()

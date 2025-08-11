from backend.app.chat.agent.utils.schemas import Plan
from openai import OpenAI
from openai.types.responses import ParsedResponse


class PlannerAgent:
    def __init__(
        self,
        dev_prompt,
        llm,
        messages,
        tools: list[dict] = [],
        model_name: str = "gpt-4.1-mini",
    ):
        self.model_name: str = model_name
        self.dev_prompt: str = dev_prompt
        self.llm: OpenAI = llm
        self.messages: list[dict] = messages
        self.tools = tools
        if self.dev_prompt:
            self.messages.append({"role": "developer", "content": self.dev_prompt})

    def set_tools(self, tools: list[dict]):
        self.tools = tools

    def add_messages(self, query: str):
        self.messages.append({"role": "user", "content": query})

    def plan(self, query: str) -> ParsedResponse[Plan]:
        """Create a detailed plan to complete the request of the user.

        Args:
            query (str): The request of the user.

        Returns:
            Plan: The plan to complete the request of the user.
        """
        self.add_messages(query=query)
        response = self.llm.responses.parse(
            model=self.model_name,
            input=self.messages,
            tools=self.tools,
            text_format=Plan,
        )
        return response

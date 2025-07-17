from openai import OpenAI


class OpenAi:
    """ """

    def __init__(self, model_name: str, api_key: str) -> None:
        """
        Args:
            None
        Returns:
            None
        """
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key)

    def create_response(self, messages: list, tools: list = None) -> OpenAI.responses:
        """
        Create a response from the model based on the input messages and optional tools.
        """
        return self.client.responses.create(
            model=self.model_name,
            input=messages,
            tools=tools,
            tool_choice="auto",
        )

    def parse_response(
        self, messages: list, tools: list = None, response_format=None
    ) -> OpenAI.responses:
        """
        Parse the response from the model based on the input messages, optional tools, and desired response format.
        """
        return self.client.responses.parse(
            model=self.model_name,
            input=messages,
            tools=tools,
            tool_choice="auto",
            text_format=response_format,
        )

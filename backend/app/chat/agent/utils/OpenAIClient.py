from openai import OpenAI


class OpenAIClient:
    def __init__(self, api_key: str) -> None:
        """
        Args:
            model_name: The name of the openai model we are using
            api_key: The api key for our openai model
        Returns:
        """
        self.client = OpenAI(api_key=api_key)

    def get_client(self) -> OpenAI:
        """
        Args:
            None

        Returns:
            The openai client
        """
        return self.client

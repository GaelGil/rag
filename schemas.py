from pydantic import BaseModel, Field


class Answer(BaseModel):
    text: str = Field(description="The answer to the user query as text")
    tool_used: list = Field(description="The list of tools used to get this answer")


# class

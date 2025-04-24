"""Tool class validate initial parameters"""

from typing import Any, Callable, Type

from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic.v1 import BaseModel


class ToolResult(BaseModel):
    content: str
    success: bool


class Tool(BaseModel):
    """Blueprint for creating and managing various tools that the agent can
    utilize to perform specific tasks. It is designed to handle input validation,
    execute the tool's function, and return the result in a standardized format.
    """

    name: str
    model: Type[BaseModel]
    function: Callable
    validate_missing: bool = False

    class Config:
        arbitrary_types_allowed = True

    def run(self, **kwargs) -> ToolResult:
        """Responsible for executing the tool’s function with the provided input arguments"""
        if self.validate_missing:
            missing_values = self.validate_input(**kwargs)
            if missing_values:
                content = f"Missing values: {', '.join(missing_values)}"
                return ToolResult(content=content, success=False)
        result = self.function(**kwargs)
        return ToolResult(content=str(result), success=True)

    def validate_input(self, **kwargs) -> list[str]:
        """compares the input arguments passed to the tool with the expected input
        schema defined in the `model`"""
        misssing_values = []
        for key in self.model.__fields__.keys():
            if key not in kwargs:
                misssing_values.append(key)
        return misssing_values

    @property
    def openai_tool_schema(self) -> dict[str, Any]:
        """Convert the model to the OpenAI tool schema format. Additionally, it
        removes the `"required"` key from the schema, making all input parameters
        optional. This allows the agent to provide only the available information
        without the need to hallucinate missing values."""
        schema = convert_to_openai_tool(self.model)
        schema["function"]["name"] = self.name
        if schema["function"]["parameters"].get("required"):
            del schema["function"]["parameters"]["required"]
        return schema

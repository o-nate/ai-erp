"""Base class for tools"""

from typing import Any, Callable, Type, Union

from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel

from configs.logging_config import get_logger
from tools.convert import convert_to_openai_tool

logger = get_logger(__name__)


class ToolResult(BaseModel):
    content: str
    success: bool


class Tool(BaseModel):
    """Blueprint for creating and managing various tools that the agent can
    utilize to perform specific tasks. It is designed to handle input validation,
    execute the tool's function, and return the result in a standardized format.
    """

    name: str
    model: Union[Type[BaseModel], Type[SQLModel], None]
    function: Callable
    validate_missing: bool = True
    parse_model: bool = False
    exclude_keys: list[str] = ["id"]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def run(self, **kwargs):
        """Responsible for executing the tool's function with the provided input arguments"""
        logger.debug("Running tool %s with kwargs: %s", self.name, kwargs)
        logger.debug("Type of self.function: %s", type(self.function))
        import inspect

        try:
            logger.debug(
                "Signature of self.function: %s", inspect.signature(self.function)
            )
            missing_values = self.validate_input(**kwargs)
            if missing_values:
                content = f"Missing values: {', '.join(missing_values)}"
                return ToolResult(content=content, success=False)
            result = self.function(**kwargs)
            return ToolResult(content=str(result), success=True)
        except Exception as e:
            logger.error("Error running tool %s: %s", self.name, str(e))
            return ToolResult(
                content="An error occurred while running the tool", success=False
            )

    def validate_input(self, **kwargs) -> list[str]:
        """Compares the input arguments passed to the tool with the expected input
        schema defined in the `model`"""
        if not self.validate_missing or not self.model:
            return []
        model_keys = set(self.model.__annotations__.keys()) - set(self.exclude_keys)
        input_keys = set(kwargs.keys())
        misssing_values = model_keys - input_keys
        return list(misssing_values)

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
        schema["function"]["parameters"]["properties"] = {
            key: value
            for key, value in schema["function"]["parameters"]["properties"].items()
            if key not in self.exclude_keys
        }
        return schema

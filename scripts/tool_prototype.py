"""Expense tracking prototype"""

# %%
import json
from datetime import datetime
from typing import Any, Callable, Type

from langchain_core.utils.function_calling import convert_to_openai_tool
from openai import OpenAI
from pydantic.v1 import BaseModel, validator


class Expense(BaseModel):
    description: str
    net_amount: float
    gross_amount: float
    tax_rate: float
    date: datetime


class Report(BaseModel):
    report: str


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


def add_expense_func(**kwargs):
    return f"Added: expense: {kwargs} to the database."


def report_func(report: str = None):
    return f"Reported: {report}"


# * Helper functions
def get_tool_from_response(response, tools):
    tool_name = response.choices[0].message.tool_calls[0].function.name
    for t in tools:
        if t.name == tool_name:
            return t
    raise ValueError(f"Tool {tool_name} not found in tools list.")


def parse_function_args(response):
    message = response.choices[0].message
    return json.loads(message.tool_calls[0].function.arguments)


def run_tool_from_response(response, tools):
    tool = get_tool_from_response(response, tools)
    tool_kwargs = parse_function_args(response)
    return tool.run(**tool_kwargs)


# %%
SYSTEM_MESSAGE = """You are tasked with comleting specific objectives and must report
the outcomes. At your disposal, you have a variety of tools, each specialized in 
performing a distinct type of task.

For successful task completion:
Thought: Consider the task at hand and determine which tool is best suited based on 
its capabilities and the nature of the work.

Use the report_tool with an instruction detailing the results of your work. If you 
encounter an issue and cannot complete the task:

Use the report_tool to communicate the challenge or reason for the task's incompletion.

You will receive feedback based on the outcomes of each tool's task execution or 
explanations for any tasks that couldn't be completed. This feedback loop is crucial 
for addressing and resolving any issues by strategically deploying the available tools.
"""

user_message = (
    "I have spend 5$ on a coffee today please track my expense. The tax rate is 0.2."
)

# %%
add_expense_tool = Tool(
    name="add_expense_tool",
    model=Expense,
    function=add_expense_func,
    validate_missing=True,
)

report_tool = Tool(
    name="report_tool", model=Report, function=report_func, validate_missing=True
)

tools = [add_expense_tool, report_tool]

client = OpenAI()
model_name = "gpt-3.5-turbo-0125"
messages = [
    {"role": "system", "content": SYSTEM_MESSAGE},
    {"role": "user", "content": user_message},
]

response = client.chat.completions.create(
    model=model_name,
    messages=messages,
    tools=[tool.openai_tool_schema for tool in tools],
)

tool_result = run_tool_from_response(response, tools=tools)
print(tool_result)

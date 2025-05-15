"""Expense tracking prototype"""

# %%
import json
from datetime import datetime
from typing import Any, Callable, Type

import colorama
from colorama import Fore
from langchain_core.utils.function_calling import convert_to_openai_tool
from openai import OpenAI
from pydantic.v1 import BaseModel, validator

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
MODEL = "gpt-4o-mini"
MAX_STEPS = 7
COLOR = "green"


class Expense(BaseModel):
    description: str
    net_amount: float
    gross_amount: float
    tax_rate: float
    date: datetime
    vendor: str


class Report(BaseModel):
    report: str


class DateTool(BaseModel):
    x: str = None


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


class StepResult(BaseModel):
    event: str
    content: str
    success: bool


class OpenAIAgent:
    def __init__(
        self,
        tools: list[Tool],
        client: OpenAI,
        system_message: str = SYSTEM_MESSAGE,
        model_name: str = MODEL,
        max_steps: int = MAX_STEPS,
        verbose: bool = True,
    ):
        self.tools = tools
        self.client = client
        self.model_name = model_name
        self.system_message = system_message
        self.step_history = []
        self.max_steps = max_steps
        self.verbose = verbose

    def to_console(self, tag: str, message: str, color: str = COLOR):
        if self.verbose:
            color_prefix = Fore.__dict__[color.upper()]
            print(color_prefix + f"{tag}: {message}{colorama.Style.RESET_ALL}")

    def run(self, user_input: str):
        openai_tools = [tool.openai_tool_schema for tool in self.tools]
        self.step_history = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": user_input},
        ]

        step_result = None
        i = 0

        self.to_console("START", f"Starting agent with input: {user_input}")

        while i < self.max_steps:
            step_result = self.run_step(self.step_history, openai_tools)

            if step_result.event == "finish":
                break
            elif step_result.event == "error":
                self.to_console(step_result.event, step_result.content, "red")
            else:
                self.to_console(step_result.event, step_result.content, "yellow")
            i += 1

        self.to_console("Final Result", step_result.content, COLOR)
        return step_result.content

    def run_step(self, messages: list[dict], tools):

        # Plan next step
        response = self.client.chat.completions.create(
            model=self.model_name, messages=messages, tools=tools
        )
        self.step_history.append(response.choices[0].message)

        # Check if tool call is present
        if not response.choices[0].message.tool_calls:
            return StepResult(
                event="Error", content="No tool calls were returned", success=False
            )

        tool_name = response.choices[0].message.tool_calls[0].function.name
        tool_kwargs = parse_function_args(response)

        # Execute tool call
        self.to_console(
            "Tool Call", f"Name: {tool_name}\nArgs: {tool_kwargs}", "magenta"
        )
        tool_result = run_tool_from_response(response, tools=self.tools)
        tool_result_msg = self.tool_call_message(response, tool_result)
        self.step_history.append(tool_result_msg)

        if tool_result.success:
            step_result = StepResult(
                event="tool_result", content=tool_result.content, success=True
            )
        else:
            step_result = StepResult(
                event="error", content=tool_result.content, success=False
            )

        return step_result

    def tool_call_message(self, response, tool_result: ToolResult):
        tool_call = response.choices[0].message.tool_calls[0]
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_call.function.name,
            "content": tool_result.content,
        }


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
add_expense_tool = Tool(
    name="add_expense_tool",
    model=Expense,
    function=add_expense_func,
    validate_missing=True,
)

report_tool = Tool(
    name="report_tool", model=Report, function=report_func, validate_missing=True
)

get_date_tool = Tool(
    name="get_current_date",
    model=DateTool,
    function=lambda: datetime.now().strftime("%Y-%m-%d"),
    validate_missing=False,
)

tools = [add_expense_tool, report_tool, get_date_tool]

client = OpenAI()
agent = OpenAIAgent(tools, client)
agent.run(
    user_input="I have spend 5$ on a coffee today please track my expense. The tax rate is 0.2."
)

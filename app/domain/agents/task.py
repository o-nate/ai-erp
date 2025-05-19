"""Tool wrapper for OpenAI subagents"""

from typing import Type, Callable, Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import OpenAIAgent

from ..tools.base import Tool
from ..tools.convert import convert_to_openai_tool
from ..tools.report_tool import report_tool

SYSTEM_MESSAGE = """You are tasked with completing specific objectives and must report the outcomes. At your disposal, you have a variety of tools, each specialized in performing a distinct type of task.

For successful task completion:
1. First, use the appropriate tool to perform the main task (e.g., add_expense_tool for expenses)
2. Then, use the report_tool to communicate the result to the user

For expense handling:
1. Use add_expense_tool to add the expense to the database
2. The tool will automatically calculate the gross amount if you provide:
   - description
   - net_amount
   - tax_rate
   - date
3. After the expense is added, use report_tool to inform the user of the result

IMPORTANT: When calling a tool, you MUST include all required parameters in the tool call. For example:
{{
    "description": "office supplies",
    "net_amount": 5.0,
    "gross_amount": 5.95,
    "tax_rate": 0.19,
    "date": "2025-05-08"
}}

If you encounter an issue and cannot complete the task:
1. Use the report_tool with a clear message explaining what went wrong
2. Always provide a message parameter with your report
3. Example: report_tool(message="Failed to add expense: [specific error]")

On error: If information is missing, consider if you can deduce or calculate the missing information and repeat the tool call with more arguments.

Use the information provided by the user to deduce the correct tool arguments.

Before using a tool, think about the arguments, and explain each input argument used in the tool.

Return only one tool call at a time! Explain your thoughts!

{context}
"""


class EmptyArgModel(BaseModel): ...


class TaskAgent(BaseModel):
    name: str
    description: str
    arg_model: Type[BaseModel] = EmptyArgModel
    access_roles: list[str] = ["all"]
    create_context: Callable = None
    create_user_context: Callable = None
    tool_loader: Callable = None
    system_message: str = SYSTEM_MESSAGE
    tools: list[Tool]
    examples: list[dict] = None
    routing_example: list[dict] = Field(default_factory=list)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def load_agent(self, **kwargs) -> OpenAIAgent:
        input_kwargs = self.arg_model(**kwargs)
        kwargs = input_kwargs.model_dump()

        if self.create_context:
            context = self.create_context(**kwargs)
        else:
            context = None

        if self.create_user_context:
            user_context = self.create_user_context(**kwargs)
        else:
            user_context = None

        if self.tool_loader:
            self.tools.extend(self.tool_loader(**kwargs))

        if report_tool not in self.tools:
            self.tools.append(report_tool)

        return OpenAIAgent(
            tools=self.tools,
            context=context,
            user_context=user_context,
            system_message=self.system_message,
            examples=self.examples,
        )

    @property
    def openai_tool_schema(self):
        return convert_to_openai_tool(
            self.arg_model, name=self.name, description=self.description
        )

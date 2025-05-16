"""Main AI agent logic"""

import colorama
from colorama import Fore
from openai import OpenAI
from pydantic import BaseModel

from agents.utils import parse_function_args, run_tool_from_response
from configs.logging_config import get_logger
from configs.model_configs import MODEL, MAX_STEPS, COLOR
from tools.base import Tool, ToolResult

logger = get_logger(__name__)


SYSTEM_MESSAGE = """You are tasked with comleting specific objectives and must report
the outcomes. At your disposal, you have a variety of tools, each specialized in 
performing a distinct type of task.

For successful task completion:
Thought: Consider the task at hand and determine which tool is best suited based on 
its capabilities and the nature of the work. If you can complete the task or 
answer a question, soley by the information provided you can use the report_tool directly.

Use the report_tool with an instruction detailing the results of your work or to answer a user question. 
If you encounter an issue and cannot complete the task:

Use the report_tool to communicate the challenge or reason for the task's incompletion.

You will receive feedback based on the outcomes of each tool's task execution or 
explanations for any tasks that couldn't be completed. This feedback loop is crucial 
for addressing and resolving any issues by strategically deploying the available tools.

Return only one tool call at a time.

{context}
"""


class StepResult(BaseModel):
    event: str
    content: str
    success: bool


class OpenAIAgent:
    def __init__(
        self,
        tools: list[Tool],
        client: OpenAI = OpenAI(),
        system_message: str = SYSTEM_MESSAGE,
        model_name: str = MODEL,
        max_steps: int = MAX_STEPS,
        verbose: bool = True,
        examples: list[dict] = None,
        context: str = None,
        user_context: str = None,
    ):
        self.tools = tools
        self.client = client
        self.model_name = model_name
        self.system_message = system_message
        self.step_history = []
        self.max_steps = max_steps
        self.verbose = verbose
        self.examples = examples or []
        self.context = context or ""
        self.user_context = user_context

    def to_console(self, tag: str, message: str, color: str = COLOR):
        if self.verbose:
            color_prefix = Fore.__dict__[color.upper()]
            print(color_prefix + f"{tag}: {message}{colorama.Style.RESET_ALL}")

    def run(self, user_input: str, context: str = None):
        openai_tools = [tool.openai_tool_schema for tool in self.tools]
        system_message = self.system_message.format(context=context)

        if self.user_context:
            context = (
                f"{self.user_context}\n{context}" if context else self.user_context
            )
        if context:
            user_input = f"{context}\n---\n\nUser Message: {user_input}"

        self.to_console("START", f"Starting agent with input: {user_input}")

        self.step_history = [
            {"role": "system", "content": self.system_message},
            *self.examples,
            {"role": "user", "content": user_input},
        ]

        step_result = None
        i = 0

        while i < self.max_steps:
            step_result = self.run_step(self.step_history, openai_tools)

            if step_result.event == "finish":
                break
            if step_result.event == "error":
                self.to_console(step_result.event, step_result.content, "red")
            else:
                self.to_console(step_result.event, step_result.content, "yellow")
            i += 1

        self.to_console("Final Result", step_result.content, COLOR)
        return step_result.content

    def run_step(self, messages: list[dict], tools):
        logger.debug("Starting run_step with messages: %s", messages)

        # Plan next step
        response = self.client.chat.completions.create(
            model=self.model_name, messages=messages, tools=tools
        )
        logger.debug("Got response from OpenAI: %s", response.choices[0].message)

        # Check for multiple tool calls
        if (
            response.choices[0].message.tool_calls
            and len(response.choices[0].message.tool_calls) > 1
        ):
            logger.warning("Multiple tool calls detected, requesting single tool call")
            messages = [
                *self.step_history,
                {
                    "role": "user",
                    "content": "Error: Please return only one tool call at a time.",
                },
            ]
            return self.run_step(messages=messages, tools=tools)

        self.step_history.append(response.choices[0].message)

        # Check if tool call is present
        if not response.choices[0].message.tool_calls:
            msg = response.choices[0].message.content
            logger.warning("No tool calls returned in response: %s", msg)
            return StepResult(
                event="Error",
                content=f"No tool calls were returned.\nMessage: {msg}",
                success=False,
            )

        tool_name = response.choices[0].message.tool_calls[0].function.name
        tool_kwargs = parse_function_args(response)
        logger.debug("Tool call detected - Name: %s, Args: %s", tool_name, tool_kwargs)

        # Execute tool call
        self.to_console(
            "Tool Call", f"Name: {tool_name}\nArgs: {tool_kwargs}", "magenta"
        )
        tool_result = run_tool_from_response(response, tools=self.tools)
        logger.debug("Tool execution result: %s", tool_result)
        tool_result_msg = self.tool_call_message(response, tool_result)
        self.step_history.append(tool_result_msg)

        if tool_name == "report_tool":
            try:
                step_result = StepResult(
                    event="finish", content=tool_result.content, success=True
                )
            except:
                logger.error("Tool result: %s", tool_result)
                raise ValueError("Report tool failed to run")

        elif tool_result.success:
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

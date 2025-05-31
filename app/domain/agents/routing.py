"""Specialized agent for routing tasks"""

import colorama

from langsmith import traceable
from langsmith.wrappers import wrap_openai

from openai import OpenAI

from .task import TaskAgent
from .utils import parse_function_args

from ...configs.model_configs import MODEL, MAX_STEPS, COLOR

SYSTEM_MESSAGE = """
You are a helpful assistant.

Role: You are an AI Assistant designed to serve as the primary point of contact for users interacting through a chat interface. 
Your primary role is to understand users' requests related to database operations and route these requests to the appropriate tool.

Capabilities: 
You have access to a variety of tools designed for Create, Read operations on a set of predefined tables in a database. 

Tables:
{table_names}

IMPORTANT WORKFLOWS:
1. For revenue entries (e.g. "I sold X for $Y to Z"):
   - Always use add_revenue_agent which handles customer verification and creation
   - Do NOT use add_customer_agent directly for revenue-related customer creation
2. For direct customer management (e.g. "Add a new customer"):
   - Use add_customer_agent
3. For expense entries (e.g. "I bought X for $Y"):
   - Use add_expense_agent
4. For queries (e.g. "Show me all customers"):
   - Use query_agent
"""

NOTES = """
Important Notes:
Always confirm the completion of the requested operation with the user.
Maintain user privacy and data security throughout the interaction.
If a request is ambiguous or lacks specific details, ask follow-up questions to clarify the user's needs.
"""

PROMPT_EXTRA = {"table_names": "expense, revenue, customer"}


class RoutingAgent:

    def __init__(
        self,
        tools: list[TaskAgent] = None,
        client: OpenAI = wrap_openai(OpenAI()),
        system_message: str = SYSTEM_MESSAGE,
        model_name: str = MODEL,
        max_steps: int = MAX_STEPS,
        verbose: bool = True,
        prompt_extra: dict = None,
        examples: list[dict] = None,
        context: str = None,
    ):
        self.tools = tools
        self.client = client
        self.model_name = model_name
        self.system_message = system_message
        self.memory = []
        self.step_history = []
        self.max_steps = max_steps
        self.verbose = verbose
        self.prompt_extra = prompt_extra or PROMPT_EXTRA
        self.examples = self.load_examples(examples)
        self.context = context or ""

    def load_examples(self, examples: list[dict] = None):
        examples = examples or []
        for agent in self.tools:
            examples.extend(agent.routing_example)
        return examples

    @traceable
    def run(self, user_input: str, employee_id: int = None, **kwargs):
        context = kwargs.get("context") or self.context
        if context:
            user_input_with_context = f"{context}\n---\n\nUser Message: {user_input}"
        else:
            user_input_with_context = user_input
        self.to_console(
            "START", f"Starting Routing Agent with input:\n'''{user_input_with_context}"
        )
        partial_variables = {**self.prompt_extra, "context": context}
        system_message = self.system_message.format(**partial_variables)

        # TODO get user roles
        messages = [
            {"role": "system", "content": system_message},
            *self.examples,
            {"role": "user", "content": user_input},
        ]

        tools = [tool.openai_tool_schema for tool in self.tools]

        response = self.client.chat.completions.create(
            model=self.model_name, messages=messages, tools=tools
        )
        self.step_history.append(response.choices[0].message)
        self.to_console("RESPONSE", response.choices[0].message.content, color="blue")
        tools_kwargs = parse_function_args(response)
        tool_name = response.choices[0].message.tool_calls[0].function.name
        self.to_console("Tool name:", tool_name)
        self.to_console("Tool args:", tools_kwargs)

        agent = self.prepare_agent(tool_name, tools_kwargs)
        return agent.run(user_input)

    def prepare_agent(self, tool_name, tool_kwargs):
        for agent in self.tools:
            if agent.name == tool_name:
                input_kwargs = agent.arg_model.model_validate(tool_kwargs)
                return agent.load_agent(**input_kwargs.model_dump())
        raise ValueError(f"Agent {tool_name} not found")

    def to_console(self, tag: str, message: str, color: str = COLOR):
        if self.verbose:
            color_prefix = colorama.Fore.__dict__[color.upper()]
            print(color_prefix + f"{tag}: {message}{colorama.Style.RESET_ALL}")

"""Demo agent for testing"""

from dotenv import load_dotenv

from ...configs.model_configs import (
    EXPENSE_AMOUNT_REMARK,
    REVENUE_AMOUNT_REMARK,
    TAX_REMARK,
)

from .routing import RoutingAgent
from .task import TaskAgent

from ..utils import generate_query_context

from ..tools.add import add_entry_to_table
from ..tools.base import Tool
from ..tools.query import QueryConfig, query_data_function

from ...persistance.models import Expense, Revenue, Customer

load_dotenv()

# * Initialize tools
add_expense_tool = Tool(
    name="add_expense_tool",
    description="Useful for adding expenses to database",
    function=add_entry_to_table(Expense),
    model=Expense,
    validate_missing=True,
    # parse_model=True,
)
add_revenue_tool = Tool(
    name="add_revenue_tool",
    description="Useful for adding revenue to database",
    function=add_entry_to_table(Revenue),
    model=Revenue,
    validate_missing=True,
    exclude_keys=["id", "customer"],
)
add_customer_tool = Tool(
    name="add_customer_tool",
    description="Useful for adding a customer to the database",
    function=add_entry_to_table(Customer),
    model=Customer,
    exclude_keys=["id", "revenues"],
)
query_data_tool = Tool(
    name="query_data_tool",
    description="Useful for performing queries on a database table",
    model=QueryConfig,
    function=query_data_function,
)

query_task_agent = TaskAgent(
    name="query_agent",
    description="An agent that can perform queries on multiple data sources",
    create_user_context=lambda: generate_query_context(Expense, Revenue, Customer),
    tools=[query_data_tool],
)
add_expense_agent = TaskAgent(
    name="add_expense_agent",
    description="An agent that can add an expense to the database",
    create_user_context=lambda: generate_query_context(Expense)
    + f"\nRemarks: {TAX_REMARK} {EXPENSE_AMOUNT_REMARK}",
    tools=[add_expense_tool],
)
add_revenue_agent = TaskAgent(
    name="add_revenue_agent",
    description="An agent that can add a revenue entry to the database",
    create_user_context=lambda: (
        generate_query_context(Revenue, Customer)
        + f"\nRemarks: {TAX_REMARK} {REVENUE_AMOUNT_REMARK}\n"
        + "IMPORTANT: Before adding revenue:\n"
        + "1. If a customer is mentioned, check if they exist using query_data_tool\n"
        + "2. If customer doesn't exist and you have their details, create them using add_customer_tool\n"
        + "3. Add the revenue with add_revenue_tool (using the customer_id from step 1 or 2)\n"
        + "4. If no customer is mentioned, proceed directly to adding revenue"
    ),
    tools=[query_data_tool, add_customer_tool, add_revenue_tool],
)
add_customer_agent = TaskAgent(
    name="add_customer_agent",
    description="An agent that can add a customer to the database",
    create_user_context=lambda: generate_query_context(Customer),
    tools=[add_customer_tool],
)

demo_agent = RoutingAgent(
    tools=[
        query_task_agent,
        add_expense_agent,
        add_revenue_agent,
        add_customer_agent,
    ]
)

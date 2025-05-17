"""Demo agent for testing"""

from configs.model_configs import (
    EXPENSE_AMOUNT_REMARK,
    REVENUE_AMOUNT_REMARK,
    TAX_REMARK,
)

from domain.agents.routing import RoutingAgent
from domain.agents.task import TaskAgent
from domain.utils import generate_query_context

from domain.tools.add import add_entry_to_table
from domain.tools.base import Tool
from domain.tools.query import QueryConfig, query_data_function

from persistance.models import Expense, Revenue, Customer

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
    # parse_model=True,
)
add_customer_tool = Tool(
    name="add_customer_tool",
    description="Useful for adding a customer to the database",
    function=add_entry_to_table(Customer),
    model=Customer,
    # parse_model=True,
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
    create_user_context=lambda: generate_query_context(Revenue)
    + f"\nRemarks: {TAX_REMARK} {REVENUE_AMOUNT_REMARK}",
    tools=[add_revenue_tool],
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

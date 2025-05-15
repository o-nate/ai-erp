"""Main script"""

from agents.routing import RoutingAgent
from agents.task import TaskAgent

from database.models import Expense, Revenue, Customer

from tools.add import add_entry_to_table
from tools.base import Tool
from tools.query import QueryConfig, query_data_function
from tools.report_tool import report_function, ReportSchema

from configs.logging_config import get_logger
from utils import generate_query_context

logger = get_logger(__name__)

TAX_RATE = 0.19
TAX_REMARK = f"The tax rate is {TAX_RATE}."
EXPENSE_AMOUNT_REMARK = (
    "The user provided the net_amount. You need to calculate the gross_amount."
)
REVENUE_AMOUNT_REMARK = """The user provide the gross_amount. You should use the 
tax rate to calculate the net_amount."""


def main() -> None:
    """Run script"""
    # * Initialize tools
    add_expense_tool = Tool(
        name="add_expense_tool",
        description="Useful for adding expenses to database",
        function=add_entry_to_table(Expense),
        model=Expense,
        validate_missing=True,
    )
    add_revenue_tool = Tool(
        name="add_revenue_tool",
        description="Useful for adding revenue to database",
        function=add_entry_to_table(Revenue),
        model=Revenue,
        validate_missing=True,
    )
    add_customer_tool = Tool(
        name="add_customer_tool",
        description="Useful for adding a customer to the database",
        function=add_entry_to_table(Customer),
        model=Customer,
    )
    query_data_tool = Tool(
        name="query_data_tool",
        description="Useful for performing queries on a database table",
        model=QueryConfig,
        function=query_data_function,
    )

    logger.debug(
        "Tools added: %s, %s, %s",
        add_expense_tool.name,
        add_revenue_tool.name,
        query_data_tool.name,
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

    routing_agent = RoutingAgent(
        tools=[
            query_task_agent,
            add_expense_agent,
            add_revenue_agent,
            add_customer_agent,
        ]
    )

    routing_agent.run("I have spent 5 € on a office stuff. Last Thursday")


if __name__ == "__main__":
    main()

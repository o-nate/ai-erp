"""Main script"""

from dotenv import load_dotenv

from agents.routing import RoutingAgent
from agents.task import TaskAgent

from database.models import Expense, Revenue, Customer

from tools.add import add_entry_to_table
from tools.base import Tool
from tools.query import QueryConfig, query_data_function

from configs.logging_config import get_logger
from configs.model_configs import (
    TAX_REMARK,
    EXPENSE_AMOUNT_REMARK,
    REVENUE_AMOUNT_REMARK,
)
from utils import generate_query_context

load_dotenv()

logger = get_logger(__name__)


def main() -> None:
    """Run script"""
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

    routing_agent = RoutingAgent(
        tools=[
            query_task_agent,
            add_expense_agent,
            add_revenue_agent,
            add_customer_agent,
        ]
    )

    # routing_agent.run("I have spent 5 € on a office stuff. Last Thursday")
    # routing_agent.run(
    #     "Two weeks ago on Saturday we had a revenue of 1000 € in the shop"
    # )
    # routing_agent.run("How much revenue did we made this month?")
    routing_agent.run("How much did we spend this month?")


if __name__ == "__main__":
    main()

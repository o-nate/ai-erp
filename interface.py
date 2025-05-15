# %%
from dotenv import load_dotenv

load_dotenv()

# %%
from database.models import Expense, Revenue, Customer
from agents.task import TaskAgent
from utils import generate_query_context


print(generate_query_context(Expense, Revenue, Customer))

# %%
from database.models import Expense, Revenue, Customer
from agents.task import TaskAgent
from utils import generate_query_context

from tools.base import Tool
from tools.query import QueryConfig, query_data_function
from tools.add import add_entry_to_table

query_data_tool = Tool(
    name="query_data_tool",
    model=QueryConfig,
    function=query_data_function,
    parse_model=True,
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
    + "\nRemarks: The tax rate is 0.19. The user provide the net amount you need to calculate the gross amount.",
    tools=[
        Tool(
            name="add_expense",
            description="Add an expense to the database",
            function=add_entry_to_table(Expense),
            model=Expense,
        )
    ],
)

add_revenue_agent = TaskAgent(
    name="add_revenue_agent",
    description="An agent that can add a revenue entry to the database",
    create_user_context=lambda: generate_query_context(Revenue)
    + "\nRemarks: The tax rate is 0.19. The user provide the gross_amount you should use the tax rate to calculate the net_amount.",
    tools=[
        Tool(
            name="add_revenue",
            description="Add a revenue entry to the database",
            function=add_entry_to_table(Revenue),
            model=Revenue,
        )
    ],
)

add_customer_agent = TaskAgent(
    name="add_customer_agent",
    description="An agent that can add a customer to the database",
    create_user_context=lambda: generate_query_context(Customer),
    tools=[
        Tool(
            name="add_customer",
            description="Add a customer to the database",
            function=add_entry_to_table(Customer),
            model=Customer,
        )
    ],
)

# %%
from agents.routing import RoutingAgent

routing_agent = RoutingAgent(
    tools=[query_task_agent, add_expense_agent, add_revenue_agent, add_customer_agent]
)

# %%
routing_agent.run("I have spent 5 € on a office stuff. Last Thursday")

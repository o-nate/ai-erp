from datetime import datetime

from openai import OpenAI
from pydantic.v1 import BaseModel

from src.agent import OpenAIAgent
from src.tool import Tool

MODEL = "gpt-3.5-turbo-0125"
MAX_STEPS = 7
COLOR = "green"


class Expense(BaseModel):
    description: str
    vendor: str
    net_amount: float
    gross_amount: float
    tax_rate: float
    date: datetime


class Report(BaseModel):
    report: str


class DateTool(BaseModel):
    x: str = None


def add_expense_func(**kwargs):
    return f"Added: expense: {kwargs} to the database."


def report_func(report: str = None):
    return f"Reported: {report}"


def main() -> None:
    """Run script"""
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
    agent = OpenAIAgent(
        tools, client, model_name=MODEL, max_steps=MAX_STEPS, verbose=True
    )
    agent.run(
        user_input="I have spend 5$ on a coffee today please track my expense. The tax rate is 0.2."
    )


if __name__ == "__main__":
    main()

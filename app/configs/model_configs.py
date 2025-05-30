"""Model configurations"""

MODEL = "gpt-4o-mini"
MAX_STEPS = 7
COLOR = "green"


CONTEXT_STRING = "You can access the following tables in the database:\n"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


TAX_RATE = 0.10
TAX_REMARK = f"The tax rate is {TAX_RATE}."
EXPENSE_AMOUNT_REMARK = (
    "The user provided the net_amount. You need to calculate the gross_amount."
)
REVENUE_AMOUNT_REMARK = """The user provide the gross_amount. You should use the 
tax rate to calculate the net_amount."""

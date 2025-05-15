from pydantic import BaseModel

from tools.base import Tool


class ReportSchema(BaseModel):
    report: str


def report_function(**kwargs) -> str:
    """Report a message or result"""
    if "report" in kwargs:
        return kwargs["report"]
    elif "message" in kwargs:
        return kwargs["message"]
    elif "issue" in kwargs:
        return kwargs["issue"]
    raise ValueError("Missing required 'report', 'message', or 'issue' parameter")


report_tool = Tool(
    name="report_tool",
    model=ReportSchema,
    function=report_function,
    validate_missing=False,
    parse_model=False,
)

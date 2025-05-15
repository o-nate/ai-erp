"""Utility functions and classes"""

import types
import typing

from datetime import datetime

import sqlalchemy

from pydantic import BaseModel

from configs.logging_config import get_logger
from database.models import Expense, Revenue

logger = get_logger(__name__)

CONTEXT_STRING = "You can access the following tables in the database:\n"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def orm_model_to_string(input_model_cls: BaseModel) -> str:
    """Convert ORM model to string format for LLM usage"""

    def process_field(key, value):
        if key.startswith("__"):
            return None
        if isinstance(value, typing._GenericAlias):
            if value.__origin__ == sqlalchemy.orm.base.Mapped:
                return None
            if isinstance(value, typing._AnnotatedAlias):  # noqa
                return key, value.__origin__
            elif isinstance(value, (typing._UnionGenericAlias, types.UnionType)):
                return key, value.__args__[0]
        return key, value

    logger.debug("input_model_cls: %s", input_model_cls.__annotations__)

    fields = dict(
        filter(
            None,
            (process_field(k, v) for k, v in input_model_cls.__annotations__.items()),
        )
    )
    logger.debug("fields: %s", fields)
    for k, v in fields.items():
        logger.debug(
            "k: %s, v.__name__: %s, type: %s",
            k,
            v,
            type(v),
        )
    return ", ".join([f"{k} = <{v.__name__}>" for k, v in fields.items()])


def generate_context(*table_models) -> str:
    context_str = CONTEXT_STRING
    for table in table_models:
        context_str += f"- {table.__name__}: {orm_model_to_string(table)}\n"
    return context_str


def weekday_by_date(date: datetime, days: list[str] | None = None) -> str:
    """Extrapolate day of the week from date"""
    if days is None:
        days = DAYS
    return days[date.weekday()]


def parse_date(date: datetime) -> str:
    """Convert date object to string"""
    return date.strftime("%Y-%m-%d")


def date_to_string(date: datetime) -> str:
    """Convert complete date with weekday to string"""
    return f"{weekday_by_date(date)} {parse_date(date)}"


def generate_query_context(*table_models) -> str:
    """Provide complete query context, including talbe and date information"""
    today = f"Today is {date_to_string(datetime.now())}"
    context_str = CONTEXT_STRING
    for table in table_models:
        context_str += f"- {table.__name__}: {orm_model_to_string(table)}\n"
    return f"{today}\n{context_str}"


def main() -> None:
    """Run script"""
    logger.info(generate_query_context(Expense, Revenue))
    logger.info(generate_query_context(Expense))
    logger.info(generate_query_context(Revenue))


if __name__ == "__main__":
    main()

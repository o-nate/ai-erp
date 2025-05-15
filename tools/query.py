"""Tool for querying data from the database"""

from typing import Literal

from pydantic import BaseModel
from sqlmodel import select, Session, SQLModel

from configs.logging_config import get_logger
from database import db
from database.models import Customer, Expense, Revenue
from tools.base import ToolResult

logger = get_logger(__name__)

TABLES = {"expense": Expense, "revenue": Revenue, "customer": Customer}


class WhereStatement(BaseModel):
    column: str
    operator: Literal["eq", "gt", "lt", "gte", "lte", "ne", "ct"]
    value: str


class QueryConfig(BaseModel):
    table_name: str
    columns: list[str]
    where: list[WhereStatement | None]


def query_data_function(**kwargs) -> ToolResult:
    """Query the database through natural language"""
    query_config = QueryConfig.model_validate(kwargs)

    if query_config.table_name not in TABLES:
        return ToolResult(
            content=f"Table name {query_config.table_name} not found in database models.",
            success=False,
        )

    sql_model = TABLES[query_config.table_name]
    data = sql_query_from_config(query_config, sql_model)

    return ToolResult(content=f"Query results: {data}", success=True)


def sql_query_from_config(query_config: QueryConfig, sql_model: SQLModel) -> list:
    with Session(db.engine) as session:
        selection = []
        for column in query_config.select_columns:
            if column not in sql_model.__annotations__:
                return f"Column {column} not found in model {sql_model.__name__}"
            selection.append(getattr(sql_model, column))

        statement = select(*selection)
        where_queries = query_config.where
        if where_queries:
            for where in where_queries:
                if where.column not in sql_model.__annotations__:
                    return f"Column {where['column']} not found in model {sql_model.__name__}"

                elif where.operator == "eq":
                    statement = statement.where(
                        getattr(sql_model, where.column) == where.value
                    )
                elif where.operator == "gt":
                    statement = statement.where(
                        getattr(sql_model, where.column) > where.value
                    )
                elif where.operator == "lt":
                    statement = statement.where(
                        getattr(sql_model, where.column) < where.value
                    )
                elif where.operator == "gte":
                    statement = statement.where(
                        getattr(sql_model, where.column) >= where.value
                    )
                elif where.operator == "lte":
                    statement = statement.where(
                        getattr(sql_model, where.column) <= where.value
                    )
                elif where.operator == "ne":
                    statement = statement.where(
                        getattr(sql_model, where.column) != where.value
                    )
                elif where.operator == "ct":
                    statement = statement.where(
                        getattr(sql_model, where.column).contains(where.value)
                    )

        result = session.exec(statement=statement)
        data = result.all()
        try:
            data = [repr(d) for d in data]
        except:
            pass
    return data

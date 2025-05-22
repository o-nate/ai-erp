"""Tool for querying data from the database"""

from typing import Literal

from pydantic import BaseModel
from sqlmodel import select, Session, SQLModel
from sqlalchemy import func, literal_column

from .base import ToolResult

from ...configs.logging_config import get_logger

from ...persistance import db
from ...persistance.models import Customer, Expense, Revenue

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

    # Convert table name to lowercase for consistent lookup
    table_name_lower = query_config.table_name.lower()
    if table_name_lower not in TABLES:
        return ToolResult(
            content=f"Table name {query_config.table_name} not found in database models (looked for {table_name_lower}).",
            success=False,
        )

    sql_model = TABLES[table_name_lower]
    data = sql_query_from_config(query_config, sql_model)

    return ToolResult(content=f"Query results: {data}", success=True)


def sql_query_from_config(query_config: QueryConfig, sql_model: SQLModel) -> list:
    with Session(db.engine) as session:
        selection = []
        for column in query_config.columns:
            # Handle SQL aggregation functions
            if column.startswith("SUM(") and column.endswith(")"):
                col_name = column[4:-1].strip()
                if col_name not in sql_model.__annotations__:
                    return f"Column {col_name} not found in model {sql_model.__name__}"
                selection.append(func.sum(getattr(sql_model, col_name)))
            elif column.startswith("AVG(") and column.endswith(")"):
                col_name = column[4:-1].strip()
                if col_name not in sql_model.__annotations__:
                    return f"Column {col_name} not found in model {sql_model.__name__}"
                selection.append(func.avg(getattr(sql_model, col_name)))
            elif column.startswith("COUNT(") and column.endswith(")"):
                col_name = column[6:-1].strip()
                if col_name not in sql_model.__annotations__:
                    return f"Column {col_name} not found in model {sql_model.__name__}"
                selection.append(literal_column(f"COUNT({col_name})"))
            else:
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

"""Tool for adding data to the database"""

from typing import Callable, Type
from datetime import datetime

from sqlmodel import select, Session, SQLModel

from configs.logging_config import get_logger
from database import db
from database.models import Expense

logger = get_logger(__name__)


def add_row_to_table(model_instance: SQLModel) -> str:
    try:
        with Session(db.engine) as session:
            session.add(model_instance)
            session.commit()
            session.refresh(model_instance)
        return f"Successfully added {model_instance} to the table"
    except Exception as e:
        logger.error("Error adding row to table: %s", str(e))
        raise


def add_entry_to_table(sql_model: Type[SQLModel]) -> Callable:
    # return a Callable that takes a SQLModel instance and adds it to the table
    return lambda **data: add_row_to_table(
        model_instance=sql_model.model_validate(data)
    )


def main() -> None:
    """Run script"""
    add_expense_to_table = add_entry_to_table(Expense)
    logger.info(add_expense_to_table)


if __name__ == "__main__":
    main()

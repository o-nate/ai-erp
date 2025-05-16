"""Tool for adding data to the database"""

from typing import Callable
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


def add_entry_to_table(sql_model: SQLModel) -> Callable:
    """Takes a SQLModel instance and adds it to the table"""

    def add_entry(**data):
        try:
            # Convert date string to datetime if needed
            if "date" in data and isinstance(data["date"], str):
                data["date"] = datetime.strptime(data["date"], "%Y-%m-%d")

            # Create a new instance of the model
            instance = sql_model(**data)
            return add_row_to_table(instance)
        except Exception as e:
            logger.error("Error creating model instance: %s", str(e))
            raise

    return add_entry


def main() -> None:
    """Run script"""
    add_expense_to_table = add_entry_to_table(Expense)
    logger.info(add_expense_to_table)


if __name__ == "__main__":
    main()

"""Database models"""

from datetime import time, datetime
from typing import Optional

from pydantic import BeforeValidator, model_validator
from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship
from typing_extensions import Annotated

from .utils import numeric_validator, validate_date, validate_time

from ..configs.logging_config import get_logger
from ..configs.model_configs import TAX_RATE

logger = get_logger(__name__)


DateFormat = Annotated[datetime, BeforeValidator(validate_date)]
TimeFormat = Annotated[time, BeforeValidator(validate_time)]
Numeric = Annotated[float, BeforeValidator(numeric_validator)]


class Employee(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    first_name: str
    last_name: str
    phone: str
    address: str
    city: str
    zip: str
    country: str


class Event(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "organizer", "location", "start_date", "end_date", name="unique_event"
        ),
    )
    id: Optional[int] = Field(primary_key=True, default=None)
    organizer: str
    location: str
    start_date: DateFormat
    end_date: DateFormat
    event_type: str
    event_days: list["EventDay"] = Relationship(back_populates="event")


class EventDay(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("event_id", "date", name="unique_event_day"),)
    id: Optional[int] = Field(primary_key=True, default=None)
    event_id: int | None = Field(default=None, foreign_key="event.id")
    event: Event | None = Relationship(back_populates="event_days")

    date: DateFormat
    start_time: TimeFormat
    end_time: TimeFormat
    number_of_shifts: int
    shifts: list["Shift"] = Relationship(back_populates="event_day")


class Shift(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    event_day_id: int | None = Field(default=None, foreign_key="eventday.id")
    event_day: EventDay | None = Relationship(back_populates="shifts")
    employee_id: int | None = Field(default=None, foreign_key="employee.id")
    time_tracking_id: int | None = Field(default=None, foreign_key="timetracking.id")


class TimeTracking(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    employer_id: Optional[int] = Field(default=None, foreign_key="employee.id")
    shift_id: Optional[int] = Field(default=None, foreign_key="shift.id")
    date: DateFormat
    hours_worked: float
    start_time: TimeFormat
    end_time: TimeFormat


class Revenue(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    description: str
    net_amount: Numeric
    gross_amount: Numeric
    tax_rate: Numeric
    date: DateFormat
    customer_id: Optional[int] = Field(default=None, foreign_key="customer.id")
    customer: Optional["Customer"] = Relationship(back_populates="revenues")

    @model_validator(mode="before")
    @classmethod
    def check_net_gross(cls, data: any):
        if isinstance(data, dict):
            if "net_amount" in data and "tax_rate" in data:
                data["gross_amount"] = round(
                    data["net_amount"] * (1 + data["tax_rate"]), 2
                )
            elif "gross_amount" in data and "tax_rate" in data:
                data["net_amount"] = round(
                    data["gross_amount"] / (1 + data["tax_rate"]), 2
                )
            elif "net_amount" in data and "gross_amount" in data:
                data["tax_rate"] = round(
                    (data["gross_amount"] - data["net_amount"]) / data["net_amount"], 2
                )

        logger.debug("Data: %s", data)
        return data


class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str = Field(index=True)
    net_amount: Numeric = Field(description="The net amount of the expense")
    gross_amount: Optional[Numeric] = Field(
        default=None, description="The gross amount including tax"
    )
    tax_rate: Numeric = Field(default=TAX_RATE, description="The tax rate applied")
    date: DateFormat = Field(index=True)

    @model_validator(mode="after")
    def calculate_gross_amount(self) -> "Expense":
        """Calculate gross amount if not provided"""
        if self.gross_amount is None:
            self.gross_amount = round(self.net_amount * (1 + self.tax_rate), 2)
        return self


class Customer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company: str
    first_name: str
    last_name: str
    phone: str
    address: str
    city: str
    zip: str
    country: str
    revenues: list["Revenue"] = Relationship(back_populates="customer")


class Invoice(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    customer_id: Optional[int] = Field(default=None, foreign_key="customer.id")
    invoice_number: str
    description: str
    amount: Numeric
    tax_rate: Numeric
    date: DateFormat

"""Mock data for the database"""

import os
from pathlib import Path

from datetime import datetime, time
from sqlmodel import Session, create_engine, SQLModel, inspect

from app.persistance.db import engine
from app.persistance.models import (
    Revenue,
    Expense,
    Customer,
    Invoice,
    Employee,
    Event,
    EventDay,
    Shift,
    TimeTracking,
)

from app.configs.logging_config import get_logger
from app.configs.model_configs import TAX_RATE

logger = get_logger(__name__)

revenues = [
    {
        "id": 1,
        "description": "App development",
        "net_amount": 1000.0,
        "gross_amount": 1000.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 1, 15),
        "customer_id": 1,
    },
    {
        "id": 2,
        "description": "Economic consulting services",
        "net_amount": 2000.0,
        "gross_amount": 2000.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 2, 10),
        "customer_id": 2,
    },
    {
        "id": 3,
        "description": "Platform subscription (Annual)",
        "net_amount": 500.0,
        "gross_amount": 500.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 3, 5),
        "customer_id": 3,
    },
    {
        "id": 4,
        "description": "AI Model Development",
        "net_amount": 5000.0,
        "gross_amount": 5000.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 4, 15),
        "customer_id": 4,
    },
    {
        "id": 5,
        "description": "Data Analysis Project",
        "net_amount": 3500.0,
        "gross_amount": 3500.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 4, 20),
        "customer_id": 5,
    },
    {
        "id": 6,
        "description": "System Integration",
        "net_amount": 4200.0,
        "gross_amount": 4200.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 5, 1),
        "customer_id": 6,
    },
    {
        "id": 7,
        "description": "Technical Consulting",
        "net_amount": 2800.0,
        "gross_amount": 2800.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 5, 10),
        "customer_id": 1,
    },
    {
        "id": 8,
        "description": "Custom Software Development",
        "net_amount": 6000.0,
        "gross_amount": 6000.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 5, 15),
        "customer_id": 2,
    },
]

expenses = [
    {
        "id": 1,
        "description": "Office supplies",
        "net_amount": 300.0,
        "gross_amount": 300.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 1, 20),
    },
    {
        "id": 2,
        "description": "Cloud hosting",
        "net_amount": 150.0,
        "gross_amount": 150.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 2, 5),
    },
    {
        "id": 3,
        "description": "Travel expenses",
        "net_amount": 1200.0,
        "gross_amount": 1200.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 2, 28),
    },
    {
        "id": 4,
        "description": "Software licenses",
        "net_amount": 800.0,
        "gross_amount": 800.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 3, 15),
    },
    {
        "id": 5,
        "description": "Marketing services",
        "net_amount": 1200.0,
        "gross_amount": 1200.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 3, 20),
    },
    {
        "id": 6,
        "description": "Professional training",
        "net_amount": 2500.0,
        "gross_amount": 2500.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 4, 5),
    },
    {
        "id": 7,
        "description": "Office rent",
        "net_amount": 3000.0,
        "gross_amount": 3000.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 4, 1),
    },
    {
        "id": 8,
        "description": "Equipment maintenance",
        "net_amount": 450.0,
        "gross_amount": 450.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 4, 15),
    },
    {
        "id": 9,
        "description": "Insurance premium",
        "net_amount": 1800.0,
        "gross_amount": 1800.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 4, 20),
    },
    {
        "id": 10,
        "description": "Legal services",
        "net_amount": 2200.0,
        "gross_amount": 2200.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 5, 1),
    },
    {
        "id": 11,
        "description": "Website hosting",
        "net_amount": 200.0,
        "gross_amount": 200.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 5, 5),
    },
    {
        "id": 12,
        "description": "Employee benefits",
        "net_amount": 3500.0,
        "gross_amount": 3500.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 5, 10),
    },
    {
        "id": 13,
        "description": "Conference attendance",
        "net_amount": 1500.0,
        "gross_amount": 1500.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 5, 15),
    },
]

customers = [
    {
        "id": 1,
        "company": "Quantum Computing Solutions",
        "first_name": "Alex",
        "last_name": "Martinez",
        "phone": "+1 415-555-0123",
        "address": "100 Tech Valley Road",
        "city": "San Francisco",
        "zip": "94105",
        "country": "USA",
    },
    {
        "id": 2,
        "company": "Quantum Computing Solutions",
        "first_name": "Sophie",
        "last_name": "Dubois",
        "phone": "+33 1 23 45 67 89",
        "address": "15 Rue de la Paix",
        "city": "Paris",
        "zip": "75002",
        "country": "France",
    },
    {
        "id": 3,
        "company": "Green Energy Innovations",
        "first_name": "Marcus",
        "last_name": "Andersen",
        "phone": "+45 12 34 56 78",
        "address": "Østergade 123",
        "city": "Copenhagen",
        "zip": "1100",
        "country": "Denmark",
    },
    {
        "id": 4,
        "company": "Tech Solutions Inc.",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "123456789",
        "address": "123 Elm Street",
        "city": "Tech City",
        "zip": "45678",
        "country": "USA",
    },
    {
        "id": 5,
        "company": "Quantum Computing Solutions",
        "first_name": "Jane",
        "last_name": "Smith",
        "phone": "987654321",
        "address": "456 Oak Street",
        "city": "Innovate Town",
        "zip": "78901",
        "country": "Canada",
    },
    {
        "id": 6,
        "company": "Future Ventures",
        "first_name": "Albert",
        "last_name": "Einstein",
        "phone": "555666777",
        "address": "789 Pine Avenue",
        "city": "Science City",
        "zip": "12345",
        "country": "Germany",
    },
]

invoices = [
    {
        "id": 1,
        "customer_id": 1,
        "invoice_number": "INV-1001",
        "description": "Monthly retainer",
        "amount": 1000.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 1, 31),
    },
    {
        "id": 2,
        "customer_id": 2,
        "invoice_number": "INV-1002",
        "description": "Project completion",
        "amount": 2000.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 2, 15),
    },
    {
        "id": 3,
        "customer_id": 3,
        "invoice_number": "INV-1003",
        "description": "Software license",
        "amount": 500.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 3, 10),
    },
    {
        "id": 4,
        "customer_id": 4,
        "invoice_number": "INV-1004",
        "description": "AI Model Development",
        "amount": 5000.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 4, 15),
    },
    {
        "id": 5,
        "customer_id": 5,
        "invoice_number": "INV-1005",
        "description": "Data Analysis Project",
        "amount": 3500.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 4, 20),
    },
    {
        "id": 6,
        "customer_id": 6,
        "invoice_number": "INV-1006",
        "description": "System Integration",
        "amount": 4200.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 5, 1),
    },
    {
        "id": 7,
        "customer_id": 1,
        "invoice_number": "INV-1007",
        "description": "Technical Consulting",
        "amount": 2800.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 5, 10),
    },
    {
        "id": 8,
        "customer_id": 2,
        "invoice_number": "INV-1008",
        "description": "Custom Software Development",
        "amount": 6000.0 * (1 + TAX_RATE),
        "tax_rate": TAX_RATE,
        "date": datetime(2025, 5, 15),
    },
]

employees = [
    {
        "id": 1,
        "first_name": "John",
        "last_name": "Smith",
        "phone": "+1 555-0123",
        "address": "123 Main St",
        "city": "New York",
        "zip": "10001",
        "country": "USA",
    },
    {
        "id": 2,
        "first_name": "Marie",
        "last_name": "Dubois",
        "phone": "+33 1 23 45 67 89",
        "address": "45 Rue de Paris",
        "city": "Paris",
        "zip": "75001",
        "country": "France",
    },
    {
        "id": 3,
        "first_name": "Hans",
        "last_name": "Müller",
        "phone": "+49 30 123456",
        "address": "10 Hauptstraße",
        "city": "Berlin",
        "zip": "10115",
        "country": "Germany",
    },
]

events = [
    {
        "id": 1,
        "organizer": "Tech Conference 2025",
        "location": "Convention Center",
        "start_date": datetime(2025, 6, 1),
        "end_date": datetime(2025, 6, 3),
        "event_type": "Conference",
    },
    {
        "id": 2,
        "organizer": "Annual Team Building",
        "location": "Mountain Resort",
        "start_date": datetime(2025, 7, 15),
        "end_date": datetime(2025, 7, 16),
        "event_type": "Team Building",
    },
]

event_days = [
    {
        "id": 1,
        "event_id": 1,
        "date": datetime(2025, 6, 1),
        "start_time": time(9, 0),
        "end_time": time(17, 0),
        "number_of_shifts": 2,
    },
    {
        "id": 2,
        "event_id": 1,
        "date": datetime(2025, 6, 2),
        "start_time": time(9, 0),
        "end_time": time(17, 0),
        "number_of_shifts": 2,
    },
    {
        "id": 3,
        "event_id": 2,
        "date": datetime(2025, 7, 15),
        "start_time": time(10, 0),
        "end_time": time(16, 0),
        "number_of_shifts": 1,
    },
]

shifts = [
    {"id": 1, "event_day_id": 1, "employee_id": 1, "time_tracking_id": 1},
    {"id": 2, "event_day_id": 1, "employee_id": 2, "time_tracking_id": 2},
    {"id": 3, "event_day_id": 2, "employee_id": 1, "time_tracking_id": 3},
    {"id": 4, "event_day_id": 3, "employee_id": 3, "time_tracking_id": 4},
]

time_tracking = [
    {
        "id": 1,
        "employer_id": 1,
        "shift_id": 1,
        "date": datetime(2025, 6, 1),
        "hours_worked": 8.0,
        "start_time": time(9, 0),
        "end_time": time(17, 0),
    },
    {
        "id": 2,
        "employer_id": 2,
        "shift_id": 2,
        "date": datetime(2025, 6, 1),
        "hours_worked": 8.0,
        "start_time": time(9, 0),
        "end_time": time(17, 0),
    },
    {
        "id": 3,
        "employer_id": 1,
        "shift_id": 3,
        "date": datetime(2025, 6, 2),
        "hours_worked": 8.0,
        "start_time": time(9, 0),
        "end_time": time(17, 0),
    },
    {
        "id": 4,
        "employer_id": 3,
        "shift_id": 4,
        "date": datetime(2025, 7, 15),
        "hours_worked": 6.0,
        "start_time": time(10, 0),
        "end_time": time(16, 0),
    },
]


def all_required_tables_exist(engine) -> bool:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    required_tables = set([table.__tablename__ for table in SQLModel.__subclasses__()])
    return required_tables.issubset(existing_tables)


def main() -> None:
    """Main function to insert mock data into the database"""
    logger.debug("Entering main function in mock_data.py")
    try:
        # Local database path logic (replicating from db.py for isolation)
        DATABASE_DIRECTORY = Path(__file__).parents[1]
        TEST_DATABASE_PATH = DATABASE_DIRECTORY / "test.db"
        TEST_DATABASE_URL = "sqlite:///" + str(TEST_DATABASE_PATH)
        local_engine = create_engine(TEST_DATABASE_URL, echo=True)

        # Check if database file exists and all required tables exist
        if TEST_DATABASE_PATH.exists() and all_required_tables_exist(local_engine):
            logger.info(
                "Database and all required tables already exist. Skipping mock data insertion."
            )
            return

        logger.debug("Attempting to create database session...")
        SQLModel.metadata.create_all(local_engine)
        with Session(local_engine) as session:
            logger.debug("Database session created successfully.")
            logger.debug("Inserting mock data into the database")

            logger.debug(f"Adding {len(employees)} employee records.")
            for employee in employees:
                session.add(Employee(**employee))

            logger.debug(f"Adding {len(events)} event records.")
            for event in events:
                session.add(Event(**event))

            logger.debug(f"Adding {len(event_days)} event day records.")
            for event_day in event_days:
                session.add(EventDay(**event_day))

            logger.debug(f"Adding {len(shifts)} shift records.")
            for shift in shifts:
                session.add(Shift(**shift))

            logger.debug(f"Adding {len(time_tracking)} time tracking records.")
            for tracking in time_tracking:
                session.add(TimeTracking(**tracking))

            logger.debug(f"Adding {len(revenues)} revenue records.")
            for revenue in revenues:
                session.add(Revenue(**revenue))

            logger.debug(f"Adding {len(expenses)} expense records.")
            for expense in expenses:
                session.add(Expense(**expense))

            logger.debug(f"Adding {len(customers)} customer records.")
            for customer in customers:
                session.add(Customer(**customer))

            logger.debug(f"Adding {len(invoices)} invoice records.")
            for invoice in invoices:
                session.add(Invoice(**invoice))

            session.commit()
            logger.debug("Mock data inserted successfully and session committed.")
    except Exception as e:
        logger.error(
            f"An error occurred in mock_data.py main function: {e}", exc_info=True
        )


if __name__ == "__main__":
    main()

from datetime import datetime, timedelta
from pathlib import Path
import random

import pandas as pd
from faker import Faker

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
CUSTOMER_PATH = RAW_DATA_DIR / "customer.csv"
TRANSACTIONS_PATH = RAW_DATA_DIR / "transactions.csv"

NUM_CUSTOMERS = 1000

PROFESSIONS = [
    "Software Engineer",
    "Doctor",
    "Teacher",
    "Business Owner",
    "Government Employee",
    "Student",
    "Lawyer",
    "Farmer",
    "Marketing Manager",
    "Chartered Accountant",
]

LOCATIONS = [
    "Mumbai",
    "Delhi",
    "Bangalore",
    "Chennai",
    "Hyderabad",
    "Pune",
    "Lucknow",
    "Jaipur",
    "Agra",
    "Varanasi",
]

TRANSACTION_CATEGORIES = [
    "Food",
    "Shopping",
    "Travel",
    "Entertainment",
    "Utilities",
    "Healthcare",
    "Education",
    "Investment",
]


def generate_customer_id(index):
    return f"C{index:04d}"


def generate_phone_number(rng):
    return f"{rng.choice(['6', '7', '8', '9'])}{rng.randint(100000000, 999999999)}"


def generate_customers(num_customers=NUM_CUSTOMERS, seed=None):
    rng = random.Random(seed)
    fake = Faker("en_IN")

    if seed is not None:
        fake.seed_instance(seed)

    customers = []

    for index in range(1, num_customers + 1):
        customers.append(
            {
                "customer_id": generate_customer_id(index),
                "name": fake.name(),
                "phone_number": generate_phone_number(rng),
                "age": rng.randint(21, 65),
                "profession": rng.choice(PROFESSIONS),
                "income": rng.randint(20000, 250000),
                "marital_status": rng.choice(["Single", "Married"]),
                "location": rng.choice(LOCATIONS),
            }
        )

    return pd.DataFrame(customers)


def generate_transactions(
    customers_df,
    min_transactions=10,
    max_transactions=30,
    start_date="2025-01-01",
    max_days=365,
    seed=None,
):
    rng = random.Random(seed)
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    transactions = []

    for customer_id in customers_df["customer_id"]:
        num_transactions = rng.randint(min_transactions, max_transactions)

        for _ in range(num_transactions):
            transaction_date = start_date + timedelta(days=rng.randint(0, max_days))

            transactions.append(
                {
                    "customer_id": customer_id,
                    "transaction_date": transaction_date.strftime("%Y-%m-%d"),
                    "category": rng.choice(TRANSACTION_CATEGORIES),
                    "amount": rng.randint(100, 15000),
                }
            )

    return pd.DataFrame(transactions)


def save_dataframe(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def load_raw_data(
    customer_path=CUSTOMER_PATH,
    transactions_path=TRANSACTIONS_PATH,
):
    customers_df = pd.read_csv(customer_path)
    transactions_df = pd.read_csv(transactions_path)
    return customers_df, transactions_df


def create_raw_datasets(
    output_dir=RAW_DATA_DIR,
    num_customers=NUM_CUSTOMERS,
    seed=None,
):
    output_dir = Path(output_dir)
    customer_path = output_dir / "customer.csv"
    transactions_path = output_dir / "transactions.csv"

    customers_df = generate_customers(num_customers=num_customers, seed=seed)
    transactions_seed = seed + 1 if seed is not None else None
    transactions_df = generate_transactions(customers_df, seed=transactions_seed)

    save_dataframe(customers_df, customer_path)
    save_dataframe(transactions_df, transactions_path)

    return customers_df, transactions_df


def main():
    customers_df, transactions_df = create_raw_datasets()
    print(f"Saved {len(customers_df)} customers to {CUSTOMER_PATH}")
    print(f"Saved {len(transactions_df)} transactions to {TRANSACTIONS_PATH}")


if __name__ == "__main__":
    main()

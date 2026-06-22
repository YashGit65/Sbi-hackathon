from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CUSTOMERS_PATH = PROJECT_ROOT / "data" / "raw" / "customer.csv"
TRANSACTIONS_PATH = PROJECT_ROOT / "data" / "raw" / "transactions.csv"
PROFILE_OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "profile" / "customer_profiles.csv"


def making_profile(customers_df, transactions_df, output_path=PROFILE_OUTPUT_PATH):
    """
    Calculate expenses, investments, savings, and savings rate
    for each customer.

    Parameters:
        customers_df (pd.DataFrame)
        transactions_df (pd.DataFrame)

        output_path (str | pathlib.Path | None): CSV path where the profile
            dataset should be saved. Pass None to skip saving.

    Returns:
        pd.DataFrame
    """

    # Separate investments from other expenses
    investments = (
        transactions_df[
            transactions_df["category"] == "Investment"
        ]
        .groupby("customer_id")["amount"]
        .sum()
        .reset_index(name="investment_amount")
    )

    expenses = (
        transactions_df[
            transactions_df["category"] != "Investment"
        ]
        .groupby("customer_id")["amount"]
        .sum()
        .reset_index(name="total_expenses")
    )

    # Category-wise spending
    category_spending = (
        transactions_df
        .pivot_table(
            index="customer_id",
            columns="category",
            values="amount",
            aggfunc="sum",
            fill_value=0
        )
        .reset_index()
    )

    # Merge everything
    result = customers_df.merge(
        expenses,
        on="customer_id",
        how="left"
    )

    result = result.merge(
        investments,
        on="customer_id",
        how="left"
    )

    result = result.merge(
        category_spending,
        on="customer_id",
        how="left"
    )

    result.fillna(0, inplace=True)

    # Financial metrics
    result["savings"] = (
        result["income"]
        - result["total_expenses"]
        - result["investment_amount"]
    )

    result["savings_rate"] = (
        result["savings"]
        / result["income"]
        * 100
    ).round(2)

    if output_path is not None:
        output_path = Path(output_path)
        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_path

        output_path.parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(output_path, index=False)

    return result


def main():
    customers_df = pd.read_csv(CUSTOMERS_PATH)
    transactions_df = pd.read_csv(TRANSACTIONS_PATH)

    profile_df = making_profile(customers_df, transactions_df)
    print(f"Saved profile dataset to {PROFILE_OUTPUT_PATH}")
    print(profile_df.head())


if __name__ == "__main__":
    main()

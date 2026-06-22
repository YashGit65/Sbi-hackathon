from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GOALS_INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "profile"
    / "customer_profiles-with-goals.csv"
)

RISK_OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "customer_profile"
    / "customer_profiles.csv"
)


def risk_agent(customer_row):
    score = 0
    savings_rate = customer_row["savings_rate"]

    if abs(savings_rate) > 1:
        savings_rate = savings_rate / 100

    # Age
    if customer_row['age'] < 35:
        score += 3
    elif customer_row['age'] < 50:
        score += 2
    else:
        score += 1

    # Savings Rate
    if savings_rate > 0.30:
        score += 3
    elif savings_rate > 0.15:
        score += 2
    else:
        score += 1

    # Income
    if customer_row['income'] > 100000:
        score += 3
    elif customer_row['income'] > 50000:
        score += 2
    else:
        score += 1

    # Existing Investments
    if customer_row['investment_amount'] > 500000:
        score += 3
    elif customer_row['investment_amount'] > 100000:
        score += 2
    else:
        score += 1

    # Final Risk Profile
    if score >= 10:
        return "Aggressive"
    elif score >= 7:
        return "Moderate"
    else:
        return "Conservative"


def make_risk_dataset(input_path=GOALS_INPUT_PATH, output_path=RISK_OUTPUT_PATH):
    profiles_df = pd.read_csv(input_path)
    profiles_df["risk"] = profiles_df.apply(risk_agent, axis=1)

    output_path = Path(output_path)
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    profiles_df.to_csv(output_path, index=False)

    return profiles_df


def main():
    risk_df = make_risk_dataset()
    print(f"Saved customer profiles with risks to {RISK_OUTPUT_PATH}")
    print(risk_df.head())


if __name__ == "__main__":
    main()

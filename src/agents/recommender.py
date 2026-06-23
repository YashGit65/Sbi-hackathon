import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILE_INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "customer_profile"
    / "customer_profiles.csv"
)
RECOMMENDATION_OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "recommendation"
    / "profile-recommended.csv"
)


def recommendation_agent(row):

    income = row["income"]
    total_expenses = row["total_expenses"]
    risk = row["risk"]

    # Calculate savings
    monthly_savings = max(0, row['savings'])
    
    savings_rate = row['savings_rate']

    # Invest only 80% of savings
    investable_amount = monthly_savings * 0.8

    # Parse goals JSON
    goal_str = row["goals"]

    if isinstance(goal_str, str):
        goal_str = goal_str.replace('""', '"')
        goals = json.loads(goal_str)
    else:
        goals = goal_str

    recommendations = []

    total_confidence = sum(
        goal["confidence"] for goal in goals
    )

    for goal_data in goals:

        goal = goal_data["goal"]
        confidence = goal_data["confidence"]

        amount = round(
            investable_amount *
            (confidence / total_confidence)
        )

        # Product recommendation
        if goal == "Build Emergency Fund":

            product = "Fixed Deposit / Liquid Fund"

        elif goal == "Long-Term Wealth Creation":

            if risk == "Aggressive":
                product = "Equity Mutual Fund SIP"
            elif risk == "Moderate":
                product = "Balanced Mutual Fund SIP"
            else:
                product = "Debt Mutual Fund"

        elif goal == "Retirement Planning":

            if risk == "Aggressive":
                product = "Equity Mutual Fund SIP"
            elif risk == "Moderate":
                product = "Balanced Mutual Fund SIP"
            else:
                product = "PPF"

        elif goal == "Home Purchase":

            product = "Recurring Deposit"

        elif goal == "Child Education Planning":

            product = "Hybrid Mutual Fund"

        elif goal == "Vehicle Purchase":

            product = "Recurring Deposit"

        else:

            product = "Savings Account"

        recommendations.append({
            "goal": goal,
            "confidence": confidence,
            "product": product,
            "monthly_amount": amount
        })

    # Voice summary
    summary = (
        f"Based on your monthly income of ₹{income:,.0f}, "
        f"savings rate of {savings_rate:.1f}% "
        f"and {risk.lower()} risk profile, "
        f"we recommend the following investment strategy. "
    )

    for rec in recommendations:

        summary += (
            f"For {rec['goal']}, invest approximately "
            f"₹{rec['monthly_amount']:,.0f} per month in "
            f"{rec['product']}. "
        )

    return {
        "recommendations": recommendations
    }


def make_recommendation_dataset(
    input_path=PROFILE_INPUT_PATH,
    output_path=RECOMMENDATION_OUTPUT_PATH
):
    profiles_df = pd.read_csv(input_path)
    profiles_df["recommendation"] = profiles_df.apply(
        lambda row: json.dumps(recommendation_agent(row)),
        axis=1
    )

    output_path = Path(output_path)
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    profiles_df.to_csv(output_path, index=False)

    return profiles_df


def main():
    recommendation_df = make_recommendation_dataset()
    print(f"Saved profile recommendations to {RECOMMENDATION_OUTPUT_PATH}")
    print(recommendation_df.head())


if __name__ == "__main__":
    main()

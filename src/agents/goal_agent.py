import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILE_INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "profile" / "customer_profiles.csv"
GOALS_OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "profile"
    / "customer_profiles-with-goals.csv"
)

def detect_goals(customer):
    """
    customer -> pandas Series (one row from dataframe)

    Returns:
        List of detected goals with confidence scores
    """

    goals = []

    income = customer["income"]
    age = customer["age"]
    profession = customer["profession"]
    marital_status = customer["marital_status"]

    total_expenses = customer["total_expenses"]
    savings = customer["savings"]
    savings_rate = customer["savings_rate"] / 100
    investment_amount = customer["investment_amount"]

    # -----------------------------------
    # Emergency Fund Goal
    # -----------------------------------
    emergency_target = total_expenses * 6

    if savings < emergency_target:
        confidence = round(
            min(0.95, 1 - (savings / max(emergency_target, 1))),
            2
        )

        goals.append({
            "goal": "Build Emergency Fund",
            "confidence": confidence
        })

    # -----------------------------------
    # Wealth Creation
    # -----------------------------------
    if income >= 60000 and savings_rate >= 0.20:
        confidence = min(
            0.95,
            round(
                0.6 +
                (savings_rate * 0.5) +
                (investment_amount / max(income * 12, 1)),
                2
            )
        )

        goals.append({
            "goal": "Long-Term Wealth Creation",
            "confidence": confidence
        })

    # -----------------------------------
    # Retirement Planning
    # -----------------------------------
    if age >= 45:
        confidence = round(min(0.95, age / 60), 2)

        goals.append({
            "goal": "Retirement Planning",
            "confidence": confidence
        })

    # -----------------------------------
    # Home Purchase
    # -----------------------------------
    if 25 <= age <= 45 and savings_rate >= 0.15 and income >= 50000:
        confidence = round(
            min(
                0.90,
                0.5 + savings_rate
            ),
            2
        )

        goals.append({
            "goal": "Home Purchase",
            "confidence": confidence
        })

    # -----------------------------------
    # Child Education
    # -----------------------------------
    if marital_status == "Married" and age >= 30:
        goals.append({
            "goal": "Child Education Planning",
            "confidence": 0.75
        })

    # -----------------------------------
    # Vehicle Purchase
    # -----------------------------------
    if 25 <= age <= 40 and income >= 40000:
        goals.append({
            "goal": "Vehicle Purchase",
            "confidence": 0.65
        })

    # -----------------------------------
    # Profession Based Goals
    # -----------------------------------
    profession_map = {
        "Student": ("Higher Education", 0.90),
        "Engineer": ("Career Growth & Wealth Creation", 0.70),
        "Doctor": ("Retirement & Wealth Growth", 0.80),
        "Teacher": ("Retirement Planning", 0.75),
        "Businessman": ("Business Expansion", 0.90)
    }

    if profession in profession_map:
        goal, conf = profession_map[profession]

        goals.append({
            "goal": goal,
            "confidence": conf
        })

    # -----------------------------------
    # Spending Pattern Based Goals
    # -----------------------------------

    spending_cols = [
        "Education",
        "Entertainment",
        "Food",
        "Healthcare",
        "Investment",
        "Shopping",
        "Travel",
        "Utilities"
    ]

    largest_category = customer[spending_cols].idxmax()

    category_goal_map = {
        "Education": "Skill Development",
        "Travel": "Travel Fund",
        "Healthcare": "Medical Security",
        "Investment": "Portfolio Growth",
        "Shopping": "Lifestyle Upgrade"
    }

    if largest_category in category_goal_map:
        goals.append({
            "goal": category_goal_map[largest_category],
            "confidence": 0.70
        })

    # -----------------------------------
    # Sort & Return Top 3 Goals
    # -----------------------------------

    goals = sorted(
        goals,
        key=lambda x: x["confidence"],
        reverse=True
    )

    return goals[:3]


def make_goals_dataset(input_path=PROFILE_INPUT_PATH, output_path=GOALS_OUTPUT_PATH):
    profiles_df = pd.read_csv(input_path)
    profiles_df["goals"] = profiles_df.apply(
        lambda customer: json.dumps(detect_goals(customer)),
        axis=1
    )

    output_path = Path(output_path)
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    profiles_df.to_csv(output_path, index=False)

    return profiles_df


def main():
    goals_df = make_goals_dataset()
    print(f"Saved customer profiles with goals to {GOALS_OUTPUT_PATH}")
    print(goals_df.head())


if __name__ == "__main__":
    main()

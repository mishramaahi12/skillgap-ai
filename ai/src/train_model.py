
import pandas as pd
import joblib
import os

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error


DATA_PATH = "../data/student_attempts.csv"
MODEL_DIR = "../models"


FEATURE_COLUMNS = [
    "time_to_first_attempt",
    "total_attempts",
    "compile_count",
    "error_count",
    "hint_count",
    "repeated_error_count",
    "solution_correctness",
    "test_cases_passed",
    "time_to_solution",
    "code_changes",
]


# Tasks belonging to each skill
SKILL_TASKS = {
    "Problem_Decomposition": [
        "T004",
        "T005",
        "T014",
        "T015",
        "T016",
    ],
    "Debugging": [
        "T001",
        "T002",
        "T003",
        "T011",
        "T012",
        "T013",
    ],
    "Algorithmic_Thinking": [
        "T006",
        "T007",
        "T017",
        "T018",
        "T019",
    ],
    "Code_Quality": [
        "T008",
        "T020",
        "T021",
        "T022",
        "T023",
        "T024",
        "T025",
    ],
    "SQL_Reasoning": [
        "T009",
        "T010",
        "T026",
        "T027",
        "T028",
        "T029",
        "T030",
    ],
}


def create_target(df):
    """Create a performance target from student behavior."""

    return (
        df["solution_correctness"] * 60
        + (df["test_cases_passed"] / 10) * 25
        + (1 / df["total_attempts"].clip(lower=1)) * 15
    )


def train_skill_models(df):
    """Train one Random Forest model for each skill."""

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    for skill, task_ids in SKILL_TASKS.items():

        skill_data = df[
            df["task_id"].isin(task_ids)
        ].copy()

        if len(skill_data) < 5:
            print(
                f"Skipping {skill}: not enough data."
            )
            continue

        X = skill_data[FEATURE_COLUMNS]

        y = create_target(
            skill_data
        )

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )

        model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )

        model.fit(
            X_train,
            y_train
        )

        predictions = model.predict(
            X_test
        )

        mae = mean_absolute_error(
            y_test,
            predictions
        )

        model_path = os.path.join(
            MODEL_DIR,
            f"{skill}.pkl"
        )

        joblib.dump(
            model,
            model_path
        )

        print(
            f"{skill:<25} "
            f"MAE: {mae:.2f} "
            f"→ saved"
        )


if __name__ == "__main__":

    df = pd.read_csv(
        DATA_PATH
    )

    print(
        "\nTRAINING SKILL-SPECIFIC MODELS"
    )

    print(
        "=" * 60
    )

    train_skill_models(
        df
    )

    print(
        "=" * 60
    )

    print(
        "Training completed."
    )

    print(
        "=" * 60
    )


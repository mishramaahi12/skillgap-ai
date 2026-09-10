import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import GroupShuffleSplit
from skill_features import create_features

from xgboost import XGBRegressor


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

    # Engineered features
    "attempt_efficiency",
    "error_rate",
    "repeated_error_rate",
    "hint_dependency",
    "test_case_rate",
    "time_efficiency",
    "code_change_rate",
]


SKILL_TASKS = {
    "Problem_Decomposition": [
        "T004", "T005", "T014", "T015", "T016"
    ],
    "Debugging": [
        "T001", "T002", "T003", "T011", "T012", "T013"
    ],
    "Algorithmic_Thinking": [
        "T006", "T007", "T017", "T018", "T019"
    ],
    "Code_Quality": [
        "T008", "T020", "T021", "T022",
        "T023", "T024", "T025"
    ],
    "SQL_Reasoning": [
        "T009", "T010", "T026", "T027",
        "T028", "T029", "T030"
    ],
}


TARGET_COLUMN = "true_skill_score"


# --------------------------------------------------
# MODELS
# --------------------------------------------------

def get_models():

    return {
        "Random Forest": RandomForestRegressor(
            n_estimators=200,
            max_depth=8,
            min_samples_leaf=2,
            random_state=42
        ),

        "XGBoost": XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="reg:squarederror",
            random_state=42
        )
    }


# --------------------------------------------------
# TRAIN + COMPARE
# --------------------------------------------------

def train_and_compare(df):

    os.makedirs(MODEL_DIR, exist_ok=True)

    all_results = []

    for skill, task_ids in SKILL_TASKS.items():

        print("\n" + "-" * 60)
        print(f"Skill: {skill}")
        print("-" * 60)

        skill_data = df[
            df["task_id"].isin(task_ids)
        ].copy()

        X = skill_data[FEATURE_COLUMNS]
        y = skill_data[TARGET_COLUMN]

        splitter = GroupShuffleSplit(
            n_splits=1,
            test_size=0.2,
            random_state=42
        )

        train_indices, test_indices = next(
            splitter.split(
                X,
                y,
                groups=skill_data["student_id"]
            )
        )

        X_train = X.iloc[train_indices]
        X_test = X.iloc[test_indices]

        y_train = y.iloc[train_indices]
        y_test = y.iloc[test_indices]

        models = get_models()

        best_model = None
        best_model_name = None
        best_mae = float("inf")

        for model_name, model in models.items():

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

            print(
                f"{model_name:<18} MAE: {mae:.4f}"
            )

            all_results.append({
                "skill": skill,
                "model": model_name,
                "mae": mae
            })

            if mae < best_mae:
                best_mae = mae
                best_model = model
                best_model_name = model_name

        # Save best model for this skill
        model_path = os.path.join(
            MODEL_DIR,
            f"{skill}.pkl"
        )

        joblib.dump(
            best_model,
            model_path
        )

        print(
            f"\nBEST MODEL: {best_model_name}"
        )
        print(
            f"BEST MAE: {best_mae:.4f}"
        )
        print(
            f"SAVED: {model_path}"
        )

    return pd.DataFrame(all_results)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    df = pd.read_csv(DATA_PATH)

    df = create_features(df)

    print("\n" + "=" * 60)
    print("SKILLGAP AI - MODEL COMPARISON")
    print("=" * 60)

    print(
        f"\nDataset records : {len(df)}"
    )

    print(
        f"Students        : {df['student_id'].nunique()}"
    )

    print(
        f"Tasks           : {df['task_id'].nunique()}"
    )

    print(
        f"Target          : {TARGET_COLUMN}"
    )

    print(
        "\nComparing Random Forest vs XGBoost..."
    )

    results = train_and_compare(df)

    print("\n" + "=" * 60)
    print("MODEL COMPARISON SUMMARY")
    print("=" * 60)

    summary = results.pivot(
        index="skill",
        columns="model",
        values="mae"
    )

    print(
        summary.round(4)
    )

    print("\n" + "=" * 60)
    print("TRAINING COMPLETED")
    print("=" * 60)
import os
import joblib
import pandas as pd
import shap

from skill_features import create_features


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


SKILL_TASKS = {
    "Problem Decomposition": ["T004", "T005"],
    "Debugging": ["T001", "T002", "T003"],
    "Algorithmic Thinking": ["T006", "T007"],
    "Code Quality": ["T008"],
    "SQL Reasoning": ["T009", "T010"],
}


FEATURE_DESCRIPTIONS = {
    "time_to_first_attempt": "time before your first attempt",
    "total_attempts": "number of attempts",
    "compile_count": "number of compilation attempts",
    "error_count": "number of errors",
    "hint_count": "use of hints",
    "repeated_error_count": "repeated errors",
    "solution_correctness": "solution correctness",
    "test_cases_passed": "test cases passed",
    "time_to_solution": "time taken to reach the solution",
    "code_changes": "number of code changes",
}


NEGATIVE_FEATURES = {
    "time_to_first_attempt",
    "total_attempts",
    "compile_count",
    "error_count",
    "hint_count",
    "repeated_error_count",
    "time_to_solution",
    "code_changes",
}


def get_shap_values(model, X):
    """Calculate SHAP values."""

    explainer = shap.TreeExplainer(model)

    shap_values = explainer.shap_values(X)

    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    return shap_values


def generate_directional_explanation(
    skill,
    shap_values,
    student_data
):
    """Generate explanation using SHAP direction."""

    mean_shap = shap_values.mean(axis=0)

    explanations = []

    for index, feature in enumerate(FEATURE_COLUMNS):

        contribution = mean_shap[index]

        if contribution == 0:
            continue

        value = student_data[feature].mean()

        description = FEATURE_DESCRIPTIONS[feature]

        if contribution < 0:

            if feature in NEGATIVE_FEATURES:
                text = (
                    f"higher {description} "
                    f"lowered the predicted {skill} score"
                )
            else:
                text = (
                    f"lower {description} "
                    f"lowered the predicted {skill} score"
                )

        else:

            if feature in NEGATIVE_FEATURES:
                text = (
                    f"efficient {description} "
                    f"helped increase the predicted "
                    f"{skill} score"
                )
            else:
                text = (
                    f"better {description} "
                    f"helped increase the predicted "
                    f"{skill} score"
                )

        explanations.append({
            "feature": feature,
            "contribution": abs(contribution),
            "text": text,
            "value": value
        })

    explanations.sort(
        key=lambda x: x["contribution"],
        reverse=True
    )

    return explanations


def explain_skill(student_df, skill):

    model_name = skill.replace(" ", "_")

    model_path = os.path.join(
        MODEL_DIR,
        f"{model_name}.pkl"
    )

    if not os.path.exists(model_path):

        print(
            f"\n{skill}: Model not available yet."
        )

        return

    if student_df.empty:

        print(
            f"\n{skill}: No data available."
        )

        return

    model = joblib.load(model_path)

    X = student_df[FEATURE_COLUMNS]

    shap_values = get_shap_values(
        model,
        X
    )

    explanations = generate_directional_explanation(
        skill,
        shap_values,
        student_df
    )

    print(f"\n{skill}")
    print("-" * 70)

    print("Top SHAP factors:")

    for item in explanations[:5]:

        direction = (
            "↑ increased"
            if mean_sign(item, shap_values, item["feature"]) > 0
            else "↓ decreased"
        )

        print(
            f"  {item['feature']:<25} "
            f"{direction} prediction "
            f"({item['contribution']:.4f})"
        )

    print("\nAI Explanation:")

    for item in explanations[:3]:

        print(
            f"  • {item['text']}."
        )


def mean_sign(item, shap_values, feature):

    index = FEATURE_COLUMNS.index(feature)

    return shap_values[:, index].mean()


def explain_student(student_id="S001"):

    df = pd.read_csv(DATA_PATH)

    df = create_features(df)

    student_df = df[
        df["student_id"] == student_id
    ].copy()

    if student_df.empty:

        print(
            f"No data found for student: {student_id}"
        )

        return

    print("\n" + "=" * 70)
    print("SKILLGAP AI — DIRECTIONAL SHAP ANALYSIS")
    print("=" * 70)

    print(f"\nStudent: {student_id}")

    for skill, task_ids in SKILL_TASKS.items():

        skill_data = student_df[
            student_df["task_id"].isin(task_ids)
        ]

        explain_skill(
            skill_data,
            skill
        )

    print("\n" + "=" * 70)
    print("Directional SHAP analysis completed.")
    print("=" * 70)


if __name__ == "__main__":

    explain_student()
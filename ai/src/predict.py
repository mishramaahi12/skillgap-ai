
import os
import sys
import json
import joblib
import pandas as pd
import shap

from skill_features import create_features
from skill_gap import identify_skill_gaps, generate_roadmap


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
    "Problem Decomposition": [
        "T004", "T005", "T014", "T015", "T016"
    ],
    "Debugging": [
        "T001", "T002", "T003", "T011", "T012", "T013"
    ],
    "Algorithmic Thinking": [
        "T006", "T007", "T017", "T018", "T019"
    ],
    "Code Quality": [
        "T008", "T020", "T021", "T022", "T023", "T024", "T025"
    ],
    "SQL Reasoning": [
        "T009", "T010", "T026", "T027", "T028", "T029", "T030"
    ],
}


FEATURE_DESCRIPTIONS = {
    "time_to_first_attempt": "time before first attempt",
    "total_attempts": "number of attempts",
    "compile_count": "compilation attempts",
    "error_count": "errors",
    "hint_count": "hint usage",
    "repeated_error_count": "repeated errors",
    "solution_correctness": "solution correctness",
    "test_cases_passed": "test cases passed",
    "time_to_solution": "time taken to reach the solution",
    "code_changes": "code changes",
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


def predict_skill_score(student_data, skill):
    """Predict skill score using trained Random Forest model."""

    model_name = skill.replace(" ", "_")

    model_path = os.path.join(
        MODEL_DIR,
        f"{model_name}.pkl"
    )

    if not os.path.exists(model_path):
        return None

    model = joblib.load(model_path)

    X = student_data[FEATURE_COLUMNS]

    predictions = model.predict(X)

    score = predictions.mean()

    return round(
        max(0, min(100, score)),
        2
    )


def get_shap_explanation(student_data, skill):
    """Generate SHAP-based explanation for a skill."""

    model_name = skill.replace(" ", "_")

    model_path = os.path.join(
        MODEL_DIR,
        f"{model_name}.pkl"
    )

    if not os.path.exists(model_path):
        return []

    model = joblib.load(model_path)

    X = student_data[FEATURE_COLUMNS]

    explainer = shap.TreeExplainer(model)

    shap_values = explainer.shap_values(X)

    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    mean_shap = shap_values.mean(axis=0)

    explanations = []

    for index, feature in enumerate(FEATURE_COLUMNS):

        contribution = float(
            mean_shap[index]
        )

        if contribution == 0:
            continue

        if contribution > 0:
            direction = "positive"
        else:
            direction = "negative"

        explanations.append({
            "feature": feature,
            "description": FEATURE_DESCRIPTIONS[feature],
            "contribution": round(
                abs(contribution),
                4
            ),
            "direction": direction
        })

    explanations.sort(
        key=lambda x: x["contribution"],
        reverse=True
    )

    return explanations[:5]


def generate_explanation_text(
    skill,
    shap_results
):
    """Convert SHAP results into readable explanations."""

    explanations = []

    for item in shap_results[:3]:

        feature = item["feature"]
        description = item["description"]
        direction = item["direction"]

        if direction == "negative":

            if feature in NEGATIVE_FEATURES:
                text = (
                    f"Higher {description} "
                    f"lowered the predicted {skill} score"
                )
            else:
                text = (
                    f"Lower {description} "
                    f"lowered the predicted {skill} score"
                )

        else:

            if feature in NEGATIVE_FEATURES:
                text = (
                    f"Efficient {description} "
                    f"helped increase the predicted {skill} score"
                )
            else:
                text = (
                    f"Better {description} "
                    f"helped increase the predicted {skill} score"
                )

        explanations.append(text)

    return explanations


def predict_student(student_id="S001"):
    """Generate complete AI analysis for a student."""

    # --------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------

    df = pd.read_csv(
        DATA_PATH
    )

    # --------------------------------------------------
    # FEATURE ENGINEERING
    # --------------------------------------------------

    df = create_features(
        df
    )

    # --------------------------------------------------
    # SELECT STUDENT
    # --------------------------------------------------

    student_df = df[
        df["student_id"] == student_id
    ].copy()

    if student_df.empty:

        return {
            "error": f"No data found for student {student_id}"
        }

    # --------------------------------------------------
    # SKILL PREDICTIONS
    # --------------------------------------------------

    skill_scores = {}

    explanations = {}

    for skill, task_ids in SKILL_TASKS.items():

        skill_data = student_df[
            student_df["task_id"].isin(task_ids)
        ]

        if skill_data.empty:

            skill_scores[skill] = 0

            explanations[skill] = []

            continue

        score = predict_skill_score(
            skill_data,
            skill
        )

        if score is None:

            skill_scores[skill] = 0

            explanations[skill] = []

            continue

        skill_scores[skill] = score

        shap_results = get_shap_explanation(
            skill_data,
            skill
        )

        explanations[skill] = {
            "top_factors": shap_results,
            "summary": generate_explanation_text(
                skill,
                shap_results
            )
        }

    # --------------------------------------------------
    # SKILL GAP ANALYSIS
    # --------------------------------------------------

    gaps = identify_skill_gaps(
        skill_scores
    )

    # --------------------------------------------------
    # PERSONALIZED ROADMAP
    # --------------------------------------------------

    roadmap = generate_roadmap(
        gaps
    )

    # --------------------------------------------------
    # FINAL JSON RESULT
    # --------------------------------------------------

    result = {
        "student_id": student_id,

        "skill_scores": skill_scores,

        "skill_gaps": gaps.to_dict(
            orient="records"
        ),

        "explanations": explanations,

        "roadmap": roadmap.to_dict(
            orient="records"
        )
    }

    return result


if __name__ == "__main__":

    student_id = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "S001"
    )

    result = predict_student(
        student_id
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )


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


# ============================================================
# FEATURES
# ============================================================

FEATURE_COLUMNS = [
    # Original behavior features
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


# ============================================================
# SKILL → TASK MAPPING
# ============================================================

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
        "T008", "T020", "T021", "T022",
        "T023", "T024", "T025"
    ],

    "SQL Reasoning": [
        "T009", "T010", "T026", "T027",
        "T028", "T029", "T030"
    ],
}


# ============================================================
# FEATURE DESCRIPTIONS
# ============================================================

FEATURE_DESCRIPTIONS = {

    # Original features
    "time_to_first_attempt":
        "time before the first attempt",

    "total_attempts":
        "number of attempts",

    "compile_count":
        "compilation attempts",

    "error_count":
        "number of errors",

    "hint_count":
        "hint usage",

    "repeated_error_count":
        "repeated errors",

    "solution_correctness":
        "solution correctness",

    "test_cases_passed":
        "number of test cases passed",

    "time_to_solution":
        "time taken to reach the solution",

    "code_changes":
        "number of code changes",

    # Engineered features
    "attempt_efficiency":
        "attempt efficiency",

    "error_rate":
        "error rate",

    "repeated_error_rate":
        "repeated error rate",

    "hint_dependency":
        "hint dependency",

    "test_case_rate":
        "test case success rate",

    "time_efficiency":
        "time efficiency",

    "code_change_rate":
        "code change rate",
}


# ============================================================
# NEGATIVE FEATURES
# ============================================================

NEGATIVE_FEATURES = {

    "time_to_first_attempt",
    "total_attempts",
    "compile_count",
    "error_count",
    "hint_count",
    "repeated_error_count",
    "time_to_solution",
    "code_changes",

    "error_rate",
    "repeated_error_rate",
    "hint_dependency",
}


# ============================================================
# PREDICT SKILL SCORE
# ============================================================

def predict_skill_score(student_data, skill):

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

    score = float(predictions.mean())

    score = max(0, min(100, score))

    return round(score, 2)


# ============================================================
# SHAP EXPLANATION
# ============================================================

def get_shap_explanation(student_data, skill):

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

        contribution = float(mean_shap[index])

        if contribution == 0:
            continue

        direction = (
            "positive"
            if contribution > 0
            else "negative"
        )

        explanations.append({

            "feature": feature,

            "description":
                FEATURE_DESCRIPTIONS[feature],

            "contribution":
                round(abs(contribution), 4),

            "direction":
                direction
        })

    explanations.sort(
        key=lambda x: x["contribution"],
        reverse=True
    )

    return explanations[:5]


# ============================================================
# EXPLANATION TEXT
# ============================================================

def generate_explanation_text(
    skill,
    shap_results
):

    explanations = []

    skill_name = skill.strip()

    for item in shap_results[:3]:

        feature = item["feature"]

        description = item["description"]

        direction = item["direction"]

        if feature in NEGATIVE_FEATURES:

            if direction == "negative":

                text = (
                    f"Higher {description} negatively affected "
                    f"the predicted {skill_name} score"
                )

            else:

                text = (
                    f"Lower {description} positively contributed "
                    f"to the predicted {skill_name} score"
                )

        else:

            if direction == "positive":

                text = (
                    f"Better {description} positively contributed "
                    f"to the predicted {skill_name} score"
                )

            else:

                text = (
                    f"Lower {description} negatively affected "
                    f"the predicted {skill_name} score"
                )

        explanations.append(text)

    return explanations


# ============================================================
# MAIN STUDENT PREDICTION
# ============================================================

def predict_student(student_id="S001"):

    # Load dataset
    df = pd.read_csv(DATA_PATH)

    # Apply same feature engineering used during training
    df = create_features(df)

    # Select student
    student_df = df[
        df["student_id"] == student_id
    ].copy()

    if student_df.empty:

        return {
            "error":
                f"No data found for student {student_id}"
        }


    skill_scores = {}

    explanations = {}


    # Predict every skill
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

            "top_factors":
                shap_results,

            "summary":
                generate_explanation_text(
                    skill,
                    shap_results
                )
        }


    # Identify skill gaps
    gaps = identify_skill_gaps(
        skill_scores
    )


    # Generate roadmap
    roadmap = generate_roadmap(
        gaps
    )


    # Final result
    result = {

        "student_id":
            student_id,

        "skill_scores":
            skill_scores,

        "skill_gaps":
            gaps.to_dict(
                orient="records"
            ),

        "explanations":
            explanations,

        "roadmap":
            roadmap.to_dict(
                orient="records"
            )
    }


    return result


# ============================================================
# RUN
# ============================================================

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
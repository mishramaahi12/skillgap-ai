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
    "time_to_first_attempt": "time before the first attempt",
    "total_attempts": "number of attempts",
    "compile_count": "compilation attempts",
    "error_count": "number of errors",
    "hint_count": "hint usage",
    "repeated_error_count": "repeated errors",
    "solution_correctness": "solution correctness",
    "test_cases_passed": "number of test cases passed",
    "time_to_solution": "time taken to reach the solution",
    "code_changes": "number of code changes",

    "attempt_efficiency": "attempt efficiency",
    "error_rate": "error rate",
    "repeated_error_rate": "repeated error rate",
    "hint_dependency": "hint dependency",
    "test_case_rate": "test case success rate",
    "time_efficiency": "time efficiency",
    "code_change_rate": "code change rate",
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

    mean_values = shap_values.mean(axis=0)

    results = []

    for index, feature in enumerate(FEATURE_COLUMNS):

        contribution = float(mean_values[index])

        if contribution == 0:
            continue

        results.append({
            "feature": feature,
            "description": FEATURE_DESCRIPTIONS[feature],
            "contribution": round(contribution, 4),
            "importance": round(abs(contribution), 4),
            "direction": (
                "positive"
                if contribution > 0
                else "negative"
            )
        })

    results.sort(
        key=lambda x: x["importance"],
        reverse=True
    )

    return results[:5]


# ============================================================
# AI EXPLANATION
# ============================================================

def generate_ai_explanation(
    skill,
    shap_results,
    student_data
):

    skill = skill.strip()

    if not shap_results:
        return "Model explanation is not available yet."

    explanations = []

    for item in shap_results[:3]:

        feature = item["feature"]
        description = item["description"]
        contribution = item["contribution"]

        if feature in NEGATIVE_FEATURES:

            if contribution < 0:
                text = (
                    f"Higher {description} negatively affected "
                    f"the predicted {skill} score"
                )
            else:
                text = (
                    f"Lower {description} positively contributed "
                    f"to the predicted {skill} score"
                )

        else:

            if contribution > 0:
                text = (
                    f"Better {description} positively contributed "
                    f"to the predicted {skill} score"
                )
            else:
                text = (
                    f"Lower {description} negatively affected "
                    f"the predicted {skill} score"
                )

        explanations.append(text)

    if not explanations:
        return "No strong behavioral factors were detected."

    return "; ".join(explanations) + "."


# ============================================================
# COMPLETE AI PIPELINE
# ============================================================

def run_pipeline(student_id="S001"):

    # --------------------------------------------------------
    # 1. LOAD DATA
    # --------------------------------------------------------

    df = pd.read_csv(DATA_PATH)

    # --------------------------------------------------------
    # 2. FEATURE ENGINEERING
    # --------------------------------------------------------

    df = create_features(df)

    # --------------------------------------------------------
    # 3. SELECT STUDENT
    # --------------------------------------------------------

    student_df = df[
        df["student_id"] == student_id
    ].copy()

    if student_df.empty:

        return {
            "error": f"No data found for student {student_id}"
        }

    # --------------------------------------------------------
    # 4. ML SKILL PREDICTIONS
    # --------------------------------------------------------

    skill_scores = {}
    explanations = {}

    for skill, task_ids in SKILL_TASKS.items():

        skill_data = student_df[
            student_df["task_id"].isin(task_ids)
        ]

        if skill_data.empty:

            skill_scores[skill] = 0

            explanations[skill] = (
                "Not enough task data available."
            )

            continue

        score = predict_skill_score(
            skill_data,
            skill
        )

        if score is None:

            skill_scores[skill] = 0

            explanations[skill] = (
                "Model not trained yet."
            )

            continue

        skill_scores[skill] = score

        shap_results = get_shap_explanation(
            skill_data,
            skill
        )

        explanations[skill] = {
            "summary": generate_ai_explanation(
                skill,
                shap_results,
                skill_data
            ),
            "top_factors": shap_results
        }

    # --------------------------------------------------------
    # 5. SKILL GAP DETECTION
    # --------------------------------------------------------

    gaps = identify_skill_gaps(
        skill_scores
    )

    # --------------------------------------------------------
    # 6. PERSONALIZED ROADMAP
    # --------------------------------------------------------

    roadmap = generate_roadmap(
        gaps
    )

    # --------------------------------------------------------
    # 7. CREATE JSON-READY RESULT
    # --------------------------------------------------------

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


# ============================================================
# TERMINAL REPORT
# ============================================================

def print_report(result):

    if "error" in result:

        print(result["error"])

        return

    student_id = result["student_id"]

    skill_scores = result["skill_scores"]

    skill_gaps = result["skill_gaps"]

    explanations = result["explanations"]

    roadmap = result["roadmap"]


    print("\n" + "=" * 75)
    print("SKILLGAP AI — COMPLETE AI ANALYSIS")
    print("=" * 75)

    print(f"\nStudent: {student_id}")


    # --------------------------------------------------------
    # Skill Scores
    # --------------------------------------------------------

    print("\n" + "=" * 75)
    print("1. SKILL SCORES")
    print("=" * 75)

    for skill, score in skill_scores.items():

        print(
            f"{skill:<25} "
            f"{score:>6.2f}%"
        )


    # --------------------------------------------------------
    # Skill Gaps
    # --------------------------------------------------------

    print("\n" + "=" * 75)
    print("2. SKILL GAPS")
    print("=" * 75)

    weak_skills = [
        gap for gap in skill_gaps
        if gap["status"] == "Needs Improvement"
    ]

    if not weak_skills:

        print("No major skill gaps detected.")

    else:

        for gap in weak_skills:

            print(
                f"{gap['skill']:<25} "
                f"{gap['score']:>6.2f}% "
                f"Gap: {gap['gap']:.2f}%"
            )


    # --------------------------------------------------------
    # AI Explanations
    # --------------------------------------------------------

    print("\n" + "=" * 75)
    print("3. AI EXPLANATIONS")
    print("=" * 75)

    for skill, explanation in explanations.items():

        print(f"\n{skill}")

        print(
            f"→ {explanation['summary']}"
            if isinstance(explanation, dict)
            else f"→ {explanation}"
        )


    # --------------------------------------------------------
    # Personalized Roadmap
    # --------------------------------------------------------

    print("\n" + "=" * 75)
    print("4. PERSONALIZED SKILL ROADMAP")
    print("=" * 75)

    if not roadmap:

        print("No roadmap required.")

    else:

        for row in roadmap:

            print(
                f"\n{row['skill']} "
                f"— Current Score: "
                f"{row['current_score']}%"
            )

            steps = row[
                "learning_plan"
            ].split(" → ")

            for number, step in enumerate(
                steps,
                start=1
            ):

                print(
                    f"  {number}. {step}"
                )


    print("\n" + "=" * 75)
    print("COMPLETE AI ANALYSIS FINISHED")
    print("=" * 75)


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":

    student_id = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "S001"
    )

    result = run_pipeline(student_id)

    print_report(result)

    # Optional JSON output
    print("\n" + "=" * 75)
    print("JSON OUTPUT")
    print("=" * 75)

    print(
        json.dumps(
            result,
            indent=2
        )
    )
import os
import sys
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
    "Problem Decomposition": ["T004", "T005"],
    "Debugging": ["T001", "T002", "T003"],
    "Algorithmic Thinking": ["T006", "T007"],
    "Code Quality": ["T008"],
    "SQL Reasoning": ["T009", "T010"],
}


def predict_skill_score(student_data, skill):
    """Predict score using the trained skill model."""

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

    return round(max(0, min(100, score)), 2)


def get_shap_explanation(student_data, skill):
    """Generate top positive and negative SHAP factors."""

    model_name = skill.replace(" ", "_")
    model_path = os.path.join(
        MODEL_DIR,
        f"{model_name}.pkl"
    )

    if not os.path.exists(model_path):
        return None

    model = joblib.load(model_path)

    X = student_data[FEATURE_COLUMNS]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    mean_values = shap_values.mean(axis=0)

    results = []

    for index, feature in enumerate(FEATURE_COLUMNS):

        contribution = mean_values[index]

        results.append({
            "feature": feature,
            "contribution": contribution,
            "importance": abs(contribution)
        })

    results.sort(
        key=lambda x: x["importance"],
        reverse=True
    )

    return results


def generate_ai_explanation(
    skill,
    shap_results,
    student_data
):
    """Convert SHAP results into a student-friendly explanation."""

    if not shap_results:
        return "Model explanation is not available yet."

    explanations = []

    for item in shap_results[:3]:

        feature = item["feature"]
        contribution = item["contribution"]

        value = student_data[feature].mean()

        if contribution < 0:

            if feature in [
                "total_attempts",
                "compile_count",
                "error_count",
                "hint_count",
                "repeated_error_count",
                "time_to_first_attempt",
                "time_to_solution",
                "code_changes",
            ]:

                explanations.append(
                    f"higher {feature.replace('_', ' ')} "
                    f"lowered the predicted {skill} score"
                )

            else:

                explanations.append(
                    f"lower {feature.replace('_', ' ')} "
                    f"lowered the predicted {skill} score"
                )

        else:

            if feature in [
                "solution_correctness",
                "test_cases_passed",
            ]:

                explanations.append(
                    f"better {feature.replace('_', ' ')} "
                    f"helped increase the predicted {skill} score"
                )

            else:

                explanations.append(
                    f"efficient {feature.replace('_', ' ')} "
                    f"helped increase the predicted {skill} score"
                )

    if not explanations:
        return "No strong behavioral factors were detected."

    return "; ".join(explanations) + "."


def run_pipeline(student_id="S001"):

    # -------------------------------------------------
    # 1. LOAD DATA
    # -------------------------------------------------

    df = pd.read_csv(DATA_PATH)

    # -------------------------------------------------
    # 2. FEATURE ENGINEERING
    # -------------------------------------------------

    df = create_features(df)

    # -------------------------------------------------
    # 3. SELECT STUDENT
    # -------------------------------------------------

    student_df = df[
        df["student_id"] == student_id
    ].copy()

    if student_df.empty:

        print(
            f"No data found for student: {student_id}"
        )

        return

    # -------------------------------------------------
    # 4. ML SKILL PREDICTIONS
    # -------------------------------------------------

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

        explanations[skill] = generate_ai_explanation(
            skill,
            shap_results,
            skill_data
        )

    # -------------------------------------------------
    # 5. SKILL GAP DETECTION
    # -------------------------------------------------

    gaps = identify_skill_gaps(
        skill_scores
    )

    # -------------------------------------------------
    # 6. PERSONALIZED ROADMAP
    # -------------------------------------------------

    roadmap = generate_roadmap(
        gaps
    )

    # -------------------------------------------------
    # 7. FINAL REPORT
    # -------------------------------------------------

    print("\n" + "=" * 75)
    print("SKILLGAP AI — COMPLETE AI ANALYSIS")
    print("=" * 75)

    print(f"\nStudent: {student_id}")

    # Skill scores
    print("\n" + "=" * 75)
    print("1. SKILL SCORES")
    print("=" * 75)

    for skill, score in skill_scores.items():

        print(
            f"{skill:<25} "
            f"{score:>6.2f}%"
        )

    # Gaps
    print("\n" + "=" * 75)
    print("2. SKILL GAPS")
    print("=" * 75)

    weak_skills = gaps[
        gaps["status"] == "Needs Improvement"
    ]

    if weak_skills.empty:

        print("No major skill gaps detected.")

    else:

        for _, row in weak_skills.iterrows():

            print(
                f"{row['skill']:<25} "
                f"{row['score']:>6.2f}% "
                f"Gap: {row['gap']:.2f}%"
            )

    # Explanations
    print("\n" + "=" * 75)
    print("3. AI EXPLANATIONS")
    print("=" * 75)

    for skill, explanation in explanations.items():

        print(f"\n{skill}")
        print(f"→ {explanation}")

    # Roadmap
    print("\n" + "=" * 75)
    print("4. PERSONALIZED SKILL ROADMAP")
    print("=" * 75)

    if roadmap.empty:

        print("No roadmap required.")

    else:

        for _, row in roadmap.iterrows():

            print(
                f"\n{row['skill']} "
                f"— Current Score: {row['current_score']}%"
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


if __name__ == "__main__":

    student_id = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "S001"
    )

    run_pipeline(student_id)
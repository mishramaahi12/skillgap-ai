import pandas as pd


SKILL_COLUMNS = [
    "Problem Decomposition",
    "Debugging",
    "Algorithmic Thinking",
    "Code Quality",
    "SQL Reasoning",
]


def calculate_skill_scores(df):
    """Calculate initial skill scores from student behavior."""

    results = []

    for student_id, student_data in df.groupby("student_id"):

        scores = {
            "Problem Decomposition": 0,
            "Debugging": 0,
            "Algorithmic Thinking": 0,
            "Code Quality": 0,
            "SQL Reasoning": 0,
        }

        for _, row in student_data.iterrows():

            # Base performance score
            performance = (
                row["solution_correctness"] * 50
                + row["test_case_rate"] * 30
                + row["attempt_efficiency"] * 20
            )

            # Behavior penalties
            penalty = (
                row["repeated_error_rate"] * 15
                + row["hint_dependency"] * 10
                + row["error_rate"] * 10
            )

            final_score = max(0, min(100, performance - penalty))

            skill = None

            if row["task_id"] in ["T004", "T005"]:
                skill = "Problem Decomposition"

            elif row["task_id"] in ["T001", "T002", "T003"]:
                skill = "Debugging"

            elif row["task_id"] in ["T006", "T007"]:
                skill = "Algorithmic Thinking"

            elif row["task_id"] == "T008":
                skill = "Code Quality"

            elif row["task_id"] in ["T009", "T010"]:
                skill = "SQL Reasoning"

            if skill:
                scores[skill] += final_score

        # Average score for each skill
        skill_counts = {
            skill: 0 for skill in SKILL_COLUMNS
        }

        for _, row in student_data.iterrows():

            if row["task_id"] in ["T004", "T005"]:
                skill_counts["Problem Decomposition"] += 1

            elif row["task_id"] in ["T001", "T002", "T003"]:
                skill_counts["Debugging"] += 1

            elif row["task_id"] in ["T006", "T007"]:
                skill_counts["Algorithmic Thinking"] += 1

            elif row["task_id"] == "T008":
                skill_counts["Code Quality"] += 1

            elif row["task_id"] in ["T009", "T010"]:
                skill_counts["SQL Reasoning"] += 1

        for skill in SKILL_COLUMNS:
            if skill_counts[skill] > 0:
                scores[skill] = scores[skill] / skill_counts[skill]
            else:
                scores[skill] = 0

        results.append({
            "student_id": student_id,
            **{
                skill: round(scores[skill], 2)
                for skill in SKILL_COLUMNS
            }
        })

    return pd.DataFrame(results)


if __name__ == "__main__":

    data_path = "../data/student_attempts.csv"

    df = pd.read_csv(data_path)

    # Feature engineering
    df["attempt_efficiency"] = (
        df["solution_correctness"]
        / df["total_attempts"].clip(lower=1)
    )

    df["error_rate"] = (
        df["error_count"]
        / df["compile_count"].clip(lower=1)
    )

    df["repeated_error_rate"] = (
        df["repeated_error_count"]
        / df["error_count"].clip(lower=1)
    )

    df["hint_dependency"] = (
        df["hint_count"]
        / df["total_attempts"].clip(lower=1)
    )

    df["test_case_rate"] = df["test_cases_passed"] / 10

    scores = calculate_skill_scores(df)

    print("\nSkill Scores")
    print("=" * 70)
    print(scores.to_string(index=False))
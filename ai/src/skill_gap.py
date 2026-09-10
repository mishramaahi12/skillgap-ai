import pandas as pd


SKILL_THRESHOLDS = {
    "Problem Decomposition": 60,
    "Debugging": 60,
    "Algorithmic Thinking": 60,
    "Code Quality": 60,
    "SQL Reasoning": 60,
}


def identify_skill_gaps(skill_scores):
    """
    Identify skills that are below the required threshold.
    """

    gaps = []

    for skill, score in skill_scores.items():

        threshold = SKILL_THRESHOLDS.get(
            skill,
            60
        )

        if score < threshold:

            gap = round(
                threshold - score,
                2
            )

            gaps.append({
                "skill": skill,
                "score": round(score, 2),
                "gap": gap,
                "status": "Needs Improvement"
            })

        else:

            gaps.append({
                "skill": skill,
                "score": round(score, 2),
                "gap": 0,
                "status": "Good"
            })

    return pd.DataFrame(gaps)


def generate_roadmap(skill_gap_df):
    """
    Generate a personalized learning roadmap
    for skills that need improvement.
    """

    roadmap = {

        "Problem Decomposition": [
            "Practice breaking large problems into smaller steps",
            "Solve multi-step programming problems",
            "Write pseudocode before coding"
        ],

        "Debugging": [
            "Practice identifying syntax and logic errors",
            "Analyze error messages before changing code",
            "Solve debugging tasks without immediate hints"
        ],

        "Algorithmic Thinking": [
            "Practice searching and sorting problems",
            "Compare multiple approaches to the same problem",
            "Analyze time and space complexity"
        ],

        "Code Quality": [
            "Practice refactoring duplicate code",
            "Use meaningful variable and function names",
            "Break large functions into smaller functions"
        ],

        "SQL Reasoning": [
            "Practice filtering and aggregation queries",
            "Work with GROUP BY and JOIN operations",
            "Solve real-world SQL analysis problems"
        ]
    }

    result = []

    weak_skills = skill_gap_df[
        skill_gap_df["status"] == "Needs Improvement"
    ]

    for _, row in weak_skills.iterrows():

        skill = row["skill"]

        learning_steps = roadmap.get(
            skill,
            []
        )

        result.append({
            "skill": skill,
            "current_score": row["score"],
            "learning_plan": " → ".join(
                learning_steps
            )
        })

    return pd.DataFrame(result)
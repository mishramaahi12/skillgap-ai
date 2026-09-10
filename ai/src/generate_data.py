import random
import pandas as pd


TASKS_PATH = "../data/tasks.csv"
OUTPUT_PATH = "../data/student_attempts.csv"

random.seed(42)


# --------------------------------------------------
# STUDENT PROFILES
# --------------------------------------------------

STUDENT_PROFILES = {
    "S001": {
        "Debugging": 0.45,
        "Problem Decomposition": 0.75,
        "Algorithmic Thinking": 0.65,
        "Code Quality": 0.85,
        "SQL Reasoning": 0.55,
    },
    "S002": {
        "Debugging": 0.70,
        "Problem Decomposition": 0.45,
        "Algorithmic Thinking": 0.60,
        "Code Quality": 0.65,
        "SQL Reasoning": 0.80,
    },
    "S003": {
        "Debugging": 0.35,
        "Problem Decomposition": 0.60,
        "Algorithmic Thinking": 0.80,
        "Code Quality": 0.50,
        "SQL Reasoning": 0.45,
    },
    "S004": {
        "Debugging": 0.80,
        "Problem Decomposition": 0.70,
        "Algorithmic Thinking": 0.55,
        "Code Quality": 0.40,
        "SQL Reasoning": 0.75,
    },
    "S005": {
        "Debugging": 0.60,
        "Problem Decomposition": 0.85,
        "Algorithmic Thinking": 0.90,
        "Code Quality": 0.80,
        "SQL Reasoning": 0.65,
    },
}


def generate_attempt(student_id, task):

    skill = task["skill"]
    difficulty = task["difficulty"]

    skill_level = STUDENT_PROFILES[
        student_id
    ][skill]

    difficulty_factor = {
        "Easy": 0.00,
        "Medium": 0.12,
        "Hard": 0.25,
    }[difficulty]

    performance = max(
        0.05,
        min(
            0.98,
            skill_level - difficulty_factor
            + random.uniform(-0.08, 0.08)
        )
    )

    # Attempts
    total_attempts = max(
        1,
        round(
            1
            + (1 - performance) * 5
            + random.uniform(-0.5, 1)
        )
    )

    # Compilation attempts
    compile_count = max(
        1,
        total_attempts
        + random.randint(0, 3)
    )

    # Errors
    error_count = max(
        0,
        round(
            (1 - performance) * 8
            + random.uniform(-1, 1)
        )
    )

    # Repeated errors
    repeated_error_count = min(
        error_count,
        max(
            0,
            round(
                error_count
                * (1 - performance)
            )
        )
    )

    # Hints
    hint_count = max(
        0,
        round(
            (1 - performance) * 4
            + random.uniform(-0.5, 0.5)
        )
    )

    # Time to first attempt
    time_to_first_attempt = max(
        5,
        round(
            10
            + (1 - performance) * 70
            + random.uniform(-8, 8)
        )
    )

    # Time to solution
    time_to_solution = max(
        30,
        round(
            60
            + (1 - performance) * 700
            + difficulty_factor * 500
            + random.uniform(-40, 40)
        )
    )

    # Correctness
    solution_correctness = round(
        performance,
        2
    )

    # Test cases
    test_cases_passed = max(
        1,
        min(
            10,
            round(
                performance * 10
                + random.uniform(-1, 1)
            )
        )
    )

    # Code changes
    code_changes = max(
        1,
        round(
            total_attempts
            + error_count
            + random.uniform(0, 3)
        )
    )

    return {
        "student_id": student_id,
        "task_id": task["task_id"],
        "time_to_first_attempt": time_to_first_attempt,
        "total_attempts": total_attempts,
        "compile_count": compile_count,
        "error_count": error_count,
        "hint_count": hint_count,
        "repeated_error_count": repeated_error_count,
        "solution_correctness": solution_correctness,
        "test_cases_passed": test_cases_passed,
        "time_to_solution": time_to_solution,
        "code_changes": code_changes,
    }


def main():

    tasks = pd.read_csv(TASKS_PATH)

    records = []

    for student_id in STUDENT_PROFILES:

        for _, task in tasks.iterrows():

            record = generate_attempt(
                student_id,
                task
            )

            records.append(record)

    df = pd.DataFrame(records)

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\n" + "=" * 60)
    print("SYNTHETIC STUDENT DATA GENERATED")
    print("=" * 60)

    print(f"\nStudents : {df['student_id'].nunique()}")
    print(f"Tasks    : {df['task_id'].nunique()}")
    print(f"Attempts : {len(df)}")

    print("\nRecords per skill:")

    task_skill_map = tasks[
        ["task_id", "skill"]
    ]

    merged = df.merge(
        task_skill_map,
        on="task_id"
    )

    print(
        merged["skill"]
        .value_counts()
        .sort_index()
    )

    print(
        f"\nSaved to: {OUTPUT_PATH}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
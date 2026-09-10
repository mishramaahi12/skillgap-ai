import random
import pandas as pd

random.seed(42)

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

NUM_STUDENTS = 100

SKILLS = [
    "Debugging",
    "Problem Decomposition",
    "Algorithmic Thinking",
    "Code Quality",
    "SQL Reasoning",
]

DIFFICULTY_FACTOR = {
    "Easy": 0.00,
    "Medium": 0.10,
    "Hard": 0.20,
}

TASKS_PATH = "../data/tasks.csv"
OUTPUT_PATH = "../data/student_attempts.csv"


# --------------------------------------------------
# LOAD TASK DATA
# --------------------------------------------------

tasks = pd.read_csv(TASKS_PATH)


# --------------------------------------------------
# GENERATE STUDENT SKILL PROFILES
# --------------------------------------------------

def generate_student_profiles():
    profiles = {}

    for i in range(1, NUM_STUDENTS + 1):
        student_id = f"S{i:03d}"

        profiles[student_id] = {
            skill: round(
                random.uniform(0.30, 0.90),
                2
            )
            for skill in SKILLS
        }

    return profiles


STUDENT_PROFILES = generate_student_profiles()


# --------------------------------------------------
# GENERATE BEHAVIOR DATA
# --------------------------------------------------

records = []

for student_id, profile in STUDENT_PROFILES.items():

    for _, task in tasks.iterrows():

        skill = task["skill"]
        difficulty = task["difficulty"]

        skill_level = profile[skill]
        difficulty_factor = DIFFICULTY_FACTOR[difficulty]

        # Ground-truth skill score
        true_skill_score = round(
            skill_level * 100,
            2
        )

        # Performance depends on skill + difficulty
        performance = (
            skill_level
            - difficulty_factor
            + random.uniform(-0.04, 0.04)
        )

        performance = max(
            0.05,
            min(0.98, performance)
        )

        # ------------------------------
        # Behavioral features
        # ------------------------------

        total_attempts = max(
            1,
            round(
                1
                + (1 - performance) * 7
                + random.uniform(-1, 1)
            )
        )

        compile_count = max(
            1,
            total_attempts
            + random.randint(0, 2)
        )

        error_count = max(
            0,
            round(
                (1 - performance) * 10
                + random.uniform(-1, 1)
            )
        )

        repeated_error_count = max(
            0,
            round(
                error_count
                * (1 - performance)
                * 1.2
                + random.uniform(-0.5, 0.5)
            )
        )

        hint_count = max(
            0,
            round(
                (1 - performance) * 5
                + random.uniform(-0.5, 0.5)
            )
        )

        time_to_first_attempt = max(
            5,
            round(
                8
                + (1 - performance) * 85
                + random.uniform(-5, 5),
                2
            )
        )

        time_to_solution = max(
            30,
            round(
                50
                + (1 - performance) * 850
                + difficulty_factor * 400
                + random.uniform(-30, 30),
                2
            )
        )

        solution_correctness = round(
            performance,
            4
        )

        test_cases_passed = max(
            0,
            min(
                10,
                round(
                    performance * 10
                    + random.uniform(-1, 1)
                )
            )
        )

        code_changes = max(
            1,
            round(
                total_attempts
                + error_count * 0.8
                + random.uniform(-1, 1)
            )
        )

        records.append({
            "student_id": student_id,
            "task_id": task["task_id"],
            "true_skill_score": true_skill_score,
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
        })


# --------------------------------------------------
# SAVE DATASET
# --------------------------------------------------

df = pd.DataFrame(records)

df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\n" + "=" * 60)
print("SKILLGAP AI - SYNTHETIC DATASET GENERATED")
print("=" * 60)

print(f"\nStudents : {df['student_id'].nunique()}")
print(f"Tasks    : {df['task_id'].nunique()}")
print(f"Records  : {len(df)}")

print("\nRecords per skill:")

skill_counts = (
    tasks["skill"]
    .value_counts()
)

print(skill_counts)

print(f"\nSaved to: {OUTPUT_PATH}")

print("\n" + "=" * 60)
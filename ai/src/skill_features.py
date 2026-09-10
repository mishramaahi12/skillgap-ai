import pandas as pd


def load_student_data(file_path):
    """Load student attempt data from CSV."""
    return pd.read_csv(file_path)


def create_features(df):
    """Create ML features from raw student behavior data."""

    data = df.copy()

    # Avoid division by zero
    data["attempt_efficiency"] = (
        data["solution_correctness"] / data["total_attempts"].clip(lower=1)
    )

    data["error_rate"] = (
        data["error_count"] / data["compile_count"].clip(lower=1)
    )

    data["repeated_error_rate"] = (
        data["repeated_error_count"] / data["error_count"].clip(lower=1)
    )

    data["hint_dependency"] = (
        data["hint_count"] / data["total_attempts"].clip(lower=1)
    )

    data["test_case_rate"] = (
        data["test_cases_passed"] / 10
    )

    data["time_efficiency"] = (
        data["solution_correctness"]
        / data["time_to_solution"].clip(lower=1)
    )

    data["code_change_rate"] = (
        data["code_changes"] / data["total_attempts"].clip(lower=1)
    )

    return data


if __name__ == "__main__":
    file_path = "../data/student_attempts.csv"

    df = load_student_data(file_path)
    features = create_features(df)

    print("\nFeature Engineering Completed!")
    print("\nNew Features:")
    print(
        features[
            [
                "student_id",
                "task_id",
                "attempt_efficiency",
                "error_rate",
                "repeated_error_rate",
                "hint_dependency",
                "test_case_rate",
                "time_efficiency",
                "code_change_rate",
            ]
        ].head(10)
    )
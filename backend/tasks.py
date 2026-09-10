TASKS = {

    "task_01": {
        "title": "Find and fix the bug",
        "skill": "debugging",
        "language": "python",

        "description": (
            "The following function should return the sum "
            "of all numbers in an array. Find the problem "
            "and fix it."
        ),

        "starter_code": """def calculate_sum(numbers):
    total = 0

    for i in range(len(numbers)):
        total = numbers[i]

    return total""",

        "test_cases": [
            {
                "input": "[1, 2, 3, 4, 5]",
                "expected_output": "15"
            },
            {
                "input": "[10, 20, 30]",
                "expected_output": "60"
            },
            {
                "input": "[5]",
                "expected_output": "5"
            }
        ]
    },


    "task_02": {
        "title": "Handle the edge case",
        "skill": "debugging",
        "language": "python",

        "description": (
            "The function should return the largest number "
            "in a list. Find and fix the bug so that it also "
            "works correctly with negative numbers."
        ),

        "starter_code": """def find_largest(numbers):
    largest = 0

    for number in numbers:
        if number > largest:
            largest = number

    return largest""",

        "test_cases": [
            {
                "input": "[-5, -2, -10]",
                "expected_output": "-2"
            },
            {
                "input": "[4, 9, 2]",
                "expected_output": "9"
            },
            {
                "input": "[-1]",
                "expected_output": "-1"
            }
        ]
    },


    "task_03": {
        "title": "Break the problem into steps",
        "skill": "problem_decomposition",
        "language": "python",

        "description": (
            "Write a function that counts how many even "
            "numbers are present in a list."
        ),

        "starter_code": """def count_even(numbers):
    # Write your solution here
    pass""",

        "test_cases": [
            {
                "input": "[1, 2, 3, 4, 5, 6]",
                "expected_output": "3"
            },
            {
                "input": "[2, 4, 8]",
                "expected_output": "3"
            },
            {
                "input": "[1, 3, 5]",
                "expected_output": "0"
            }
        ]
    },


    "task_04": {
        "title": "Improve the code",
        "skill": "code_quality",
        "language": "python",

        "description": (
            "Rewrite the function so that it correctly "
            "calculates the average of the numbers in a list."
        ),

        "starter_code": """def calculate_average(numbers):
    # Write your solution here
    pass""",

        "test_cases": [
            {
                "input": "[10, 20, 30]",
                "expected_output": "20.0"
            },
            {
                "input": "[5, 10]",
                "expected_output": "7.5"
            },
            {
                "input": "[4]",
                "expected_output": "4.0"
            }
        ]
    },


    "task_05": {
        "title": "Choose the right approach",
        "skill": "problem_decomposition",
        "language": "python",

        "description": (
            "Write a function that returns the first number "
            "that appears more than once in the list. "
            "Return -1 if every number is unique."
        ),

        "starter_code": """def find_duplicate(numbers):
    # Write your solution here
    pass""",

        "test_cases": [
            {
                "input": "[1, 2, 3, 2, 4]",
                "expected_output": "2"
            },
            {
                "input": "[5, 1, 5, 2]",
                "expected_output": "5"
            },
            {
                "input": "[1, 2, 3, 4]",
                "expected_output": "-1"
            }
        ]
    }
}
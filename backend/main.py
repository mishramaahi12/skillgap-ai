from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tasks import TASKS
from docker_runner import run_python_code
from database import get_connection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "SkillGap AI Backend is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/tasks")
def get_tasks():
    task_list = []

    for task_id, task in TASKS.items():
        task_list.append({
            "task_id": task_id,
            "title": task["title"],
            "skill": task["skill"],
            "language": task["language"],
            "description": task["description"],
            "starter_code": task["starter_code"]
        })

    return {"tasks": task_list}


# ---------------------------------------------------------
# DATABASE EVENT FUNCTION
# ---------------------------------------------------------

def save_event(
    user_id,
    task_id,
    event_type,
    time_taken=0,
    runs=0,
    attempts=0,
    hints_used=0,
    test_cases_passed=0,
    test_cases_total=0
):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO assessment_events (
                user_id,
                task_id,
                event_type,
                time_taken,
                runs,
                attempts,
                hints_used,
                test_cases_passed,
                test_cases_total
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                task_id,
                event_type,
                time_taken,
                runs,
                attempts,
                hints_used,
                test_cases_passed,
                test_cases_total
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        print(f"Event saved: {event_type} - {task_id}")

        return True

    except Exception as error:
        print("Database error:", error)
        return False


# ---------------------------------------------------------
# TASK START
# ---------------------------------------------------------

@app.post("/task-start")
def task_start(data: dict):

    user_id = data.get("user_id", "demo_user")
    task_id = data.get("task_id", "task_01")

    if task_id not in TASKS:
        return {
            "success": False,
            "message": "Invalid task ID."
        }

    saved = save_event(
        user_id=user_id,
        task_id=task_id,
        event_type="task_started"
    )

    return {
        "success": saved,
        "message": "Task started."
    }


# ---------------------------------------------------------
# HINT USED
# ---------------------------------------------------------

@app.post("/hint")
def hint_used(data: dict):

    user_id = data.get("user_id", "demo_user")
    task_id = data.get("task_id", "task_01")
    time_taken = data.get("time_taken", 0)
    hints_used = data.get("hints_used", 0)

    if task_id not in TASKS:
        return {
            "success": False,
            "message": "Invalid task ID."
        }

    saved = save_event(
        user_id=user_id,
        task_id=task_id,
        event_type="hint_used",
        time_taken=time_taken,
        hints_used=hints_used
    )

    return {
        "success": saved,
        "message": "Hint usage recorded."
    }


# ---------------------------------------------------------
# RUN CODE
# ---------------------------------------------------------

@app.post("/run")
def run_code(data: dict):

    code = data.get("code", "")
    task_id = data.get("task_id", "task_01")
    user_id = data.get("user_id", "demo_user")

    time_taken = data.get("time_taken", 0)
    runs = data.get("runs", 0)
    attempts = data.get("attempts", 0)
    hints_used = data.get("hints_used", 0)

    if task_id not in TASKS:
        return {
            "success": False,
            "message": "Invalid task ID.",
            "passed": 0,
            "total": 0,
            "results": []
        }

    if not code.strip():
        return {
            "success": False,
            "message": "Please enter some code.",
            "passed": 0,
            "total": 0,
            "results": []
        }

    task = TASKS[task_id]
    test_cases = task["test_cases"]

    results = []
    passed_count = 0

    starter_code = task["starter_code"]

    function_name = starter_code.split("def ")[1].split("(")[0]

    for test in test_cases:

        test_input = test["input"]
        expected_output = test["expected_output"]

        test_program = f"""
{code}

numbers = {test_input}

result = {function_name}(numbers)

print(result)
"""

        execution = run_python_code(test_program)

        actual_output = execution["output"].strip()

        if execution["success"] and actual_output == expected_output:
            status = "passed"
            passed_count += 1
        else:
            status = "failed"

        results.append({
            "input": test_input,
            "expected": expected_output,
            "actual": actual_output,
            "status": status
        })

    total_tests = len(test_cases)

    # Save code run event
    save_event(
        user_id=user_id,
        task_id=task_id,
        event_type="code_run",
        time_taken=time_taken,
        runs=runs,
        attempts=attempts,
        hints_used=hints_used,
        test_cases_passed=passed_count,
        test_cases_total=total_tests
    )

    # Save task completion event
    if passed_count == total_tests:

        save_event(
            user_id=user_id,
            task_id=task_id,
            event_type="task_completed",
            time_taken=time_taken,
            runs=runs,
            attempts=attempts,
            hints_used=hints_used,
            test_cases_passed=passed_count,
            test_cases_total=total_tests
        )

        message = "All test cases passed!"

    else:
        message = "Some test cases failed."

    return {
        "success": True,
        "message": message,
        "passed": passed_count,
        "total": total_tests,
        "results": results,
        "task_id": task_id
    }
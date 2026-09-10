import subprocess
import tempfile
import os


def run_python_code(code: str, input_data: str = ""):
    # Create temporary Python file
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
        encoding="utf-8"
    ) as file:

        file.write(code)
        file_path = file.name

    try:
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "--memory",
                "128m",
                "--cpus",
                "0.5",
                "--pids-limit",
                "50",
                "-v",
                f"{file_path}:/app/main.py:ro",
                "python:3.12-slim",
                "python",
                "/app/main.py"
            ],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=10
        )

        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip()
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "Execution timed out."
        }

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
from docker_runner import run_python_code

code = """
print("Hello from SkillGap AI")
"""

result = run_python_code(code)

print(result)
from sandbox_runner import run_in_sandbox
import json

code = '''
import os

def solve(data):
    return os.path.exists("/var/run/docker.sock")
'''

tests = [
    {
        "input": [1],
        "expected": False
    }
]

result = run_in_sandbox(code, tests)

print("RESULT_START")
print(json.dumps(result, indent=2))
print("RESULT_END")

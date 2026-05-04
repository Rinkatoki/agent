import subprocess
import json
import os
import google.generativeai as genai


genai.configure(api_key)


# Updated model
model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")


SYSTEM_PROMPT = """
You are a coding agent working inside an existing project.
After each action, reflect on the result and decide next step carefully.

Rules:

1. Always inspect the workspace before modifying files.
2. Use "list" or "tree" if filenames are unknown.
3. Never overwrite existing files unless necessary.
4. Prefer modifying existing files instead of creating duplicates.
5. If converting a project to a framework (example: Flask),
   first read relevant files such as HTML templates to infer routes.
6. Never modify the agent's own source file unless explicitly instructed.
7. Always preserve existing functionality unless the user requests removal.
8. Always respond ONLY with valid JSON.


If a command fails or a file is missing:

1. Analyze the error message
2. Attempt a correction
3. Retry the task
4. Only finish after resolving the issue or confirming impossibility


Before writing to an existing file:

1. First read the file
2. Preserve existing content
3. Modify only what is necessary
4. Never overwrite an entire file unless explicitly instructed

Schema:

{
  "action": "run" | "write" | "read" | "finish" | "list" | "tree" | "plan",
  "command": "...",
  "filename": "...",
  "content": "...",
  "reason": "..."
}
"""




def list_tree(path="."):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            result.append(os.path.join(root, name))
    return "\n".join(result)

def list_files():
    return "\n".join(os.listdir())



BLOCKED_COMMANDS = [
    "del /f /s /q",
    "rmdir /s /q",
    "shutdown",
    "format",
    "diskpart",
    "bcdedit",
    "powershell Remove-Item",
    "Remove-Item -Recurse",
    "cipher /w",
]

def run_command(cmd):
    for blocked in BLOCKED_COMMANDS:
        if blocked in cmd:
            return "Blocked unsafe command"
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)


def read_file(filename):
    try:
        with open(filename) as f:
            return f.read()
    except:
        return "file not found"


PROTECTED_FILES = [
    "app.py",
    
]

def write_file(filename, content):
    if filename in PROTECTED_FILES:
        return "Modification blocked: protected file"
    with open(filename, "w") as f:
        f.write(content)
    return "written successfully"


def clean_json(text):
    """
    Removes ```json markdown wrappers if Gemini adds them
    """
    text = text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]

    return text.strip()


def ask_llm(history):

    prompt = SYSTEM_PROMPT + "\n\n"

    for msg in history:
        prompt += f"{msg['role']}: {msg['content']}\n"

    response = model.generate_content(prompt)

    return clean_json(response.text)


def main():

    goal = input("Enter your coding task: ")

    history = [
        {"role": "user", "content": goal}
    ]

    max_steps = 20
    steps = 0

    while steps < max_steps:

        steps += 1

        reply = ask_llm(history)

        print("\nAGENT:", reply)

        try:
            action = json.loads(reply)
        except:
            print("Invalid JSON from agent")
            break

        if action["action"] == "run":

            output = run_command(action["command"])

        elif action["action"] == "read":

            output = read_file(action["filename"])

        elif action["action"] == "write":

            output = write_file(
                action["filename"],
                action["content"]
            )
        elif action["action"] == "list":
            output = list_files()
        elif action["action"] == "tree":
            output = list_tree()

        elif action["action"] == "finish":

            print("\nDONE:", action["reason"])
            break


        else:
            output = "unknown action"

        history.append({
            "role": "assistant",
            "content": reply
        })

        history.append({
            "role": "user",
            "content": output
        })


if __name__ == "__main__":
    main()
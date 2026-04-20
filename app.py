import subprocess
import json
import os
import google.generativeai as genai


genai.configure(api_key="")


# Updated model
model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")


SYSTEM_PROMPT = """
You are a coding agent.

Always respond ONLY with valid JSON.

Never include explanations outside JSON.

Before reading or editing files, first list the directory if filenames are unknown.

Schema:

{
  "action": "run" | "write" | "read" | "finish" | "list",
  "command": "...",
  "filename": "...",
  "content": "...",
  "reason": "..."
}
"""


def list_files():
    return "\n".join(os.listdir())

def run_command(cmd):
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


def write_file(filename, content):
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
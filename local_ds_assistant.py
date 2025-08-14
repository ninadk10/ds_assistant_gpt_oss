import subprocess
import json
import pandas as pd
import os
import sys
import re

ARTIFACTS_DIR = "artifacts"
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

def extract_first_json(text):
    """Extract the first JSON object found in the text."""
    match = re.search(r"\{(?:[^{}]|(?R))*\}", text, re.S)
    if match:
        return match.group(0)
    return None

def call_ollama_with_prompt(prompt):
    """
    Send a prompt to Ollama and return parsed JSON from the first valid JSON object found.
    """
    try:
        proc = subprocess.run(
            ["ollama", "run", "gpt-oss:20b"],
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if proc.stderr and proc.stderr.strip():
            print("[Ollama stderr]", proc.stderr.strip())

        stdout = proc.stdout.strip()
        if not stdout:
            raise RuntimeError("No output from Ollama. Ensure the model is installed: `ollama pull gpt-oss:20b`.")

        json_text = extract_first_json(stdout)
        if not json_text:
            print("❌ Could not find JSON in model output. Full output:\n", stdout[:500])
            raise RuntimeError("Model did not return valid JSON.")

        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            print("❌ JSON parsing error:", e)
            print("Extracted JSON text:\n", json_text[:500])
            raise

    except FileNotFoundError:
        print("Error: Ollama is not installed or not found in PATH.")
        sys.exit(1)

def execute_code_step(code, step_num):
    """Save code to file and execute it safely."""
    script_filename = f"step_{step_num}.py"
    with open(script_filename, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"\n[Executing Step {step_num}]...")

    proc = subprocess.run(
        [sys.executable, script_filename],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if proc.stdout.strip():
        print(f"[Step {step_num} Output]\n", proc.stdout)
    if proc.stderr.strip():
        print(f"[Step {step_num} Errors]\n", proc.stderr)

def main():
    if len(sys.argv) < 2:
        print("Usage: python local_ds_assistant.py <csv_file>")
        sys.exit(1)

    csv_path = sys.argv[1]
    if not os.path.exists(csv_path):
        print(f"File {csv_path} not found.")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    print(f"Loaded CSV with shape {df.shape}. Sending a sample to the model...")

    sample_data = df.head(5).to_csv(index=False)

    prompt = f"""
You are a data science assistant.
You are given the following dataset sample:

{sample_data}

Your task:
1. Produce a JSON object with a single key "steps".
2. "steps" is an array of objects, each with:
   - "description": a short explanation of the step
   - "code": runnable Python code that uses pandas/matplotlib and saves any plots to the '{ARTIFACTS_DIR}' folder
3. Output ONLY valid JSON. No markdown, no backticks, no explanations outside JSON.
"""

    print("Calling Ollama to get analysis plan (this may take a while)...")
    plan = call_ollama_with_prompt(prompt)

    if not isinstance(plan, dict) or "steps" not in plan:
        print("Invalid plan format:", plan)
        sys.exit(1)

    print("\n📋 Analysis Plan:")
    for idx, step in enumerate(plan["steps"], start=1):
        print(f"{idx}. {step.get('description', 'No description')}")

    for idx, step in enumerate(plan["steps"], start=1):
        execute_code_step(step.get("code", ""), idx)

if __name__ == "__main__":
    main()

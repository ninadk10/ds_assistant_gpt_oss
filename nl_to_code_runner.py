import os
import sys
import subprocess
from datetime import datetime
import re

# -------------------------
# Config
# -------------------------
ARTIFACTS_DIR = "artifacts"
LOGS_DIR = "logs"
MODEL_NAME = os.environ.get("OLLAMA_MODEL", "gpt-oss:20b")

os.makedirs(ARTIFACTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


# -------------------------
# Helpers
# -------------------------
def _ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def log_text(filename: str, content: str) -> str:
    path = os.path.join(LOGS_DIR, f"{filename}_{_ts()}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def extract_first_code_block(text: str) -> str:
    """
    Extracts the first code block from model output.
    Prefers ```python fenced blocks, falls back to triple backticks,
    and finally to best-effort code lines.
    """
    # Try ```python fenced block
    match = re.search(r"```python\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Try generic triple backticks
    match = re.search(r"```(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: assume everything is code if it looks like Python
    lines = []
    for line in text.splitlines():
        if line.strip().startswith("#") or line.strip() or "import " in line or "=" in line:
            lines.append(line)
    return "\n".join(lines).strip()


# -------------------------
# Ollama call
# -------------------------
def call_ollama(prompt: str) -> str:
    """Send prompt to Ollama and return stdout."""
    proc = subprocess.run(
        ["ollama", "run", MODEL_NAME],
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    log_text("ollama_stdout_raw", stdout or "<EMPTY>")
    if stderr:
        log_text("ollama_stderr", stderr)

    return stdout


# -------------------------
# Execution
# -------------------------
def execute_code(code: str, tag: str):
    """Save code to a file and execute it."""
    script_path = os.path.join(ARTIFACTS_DIR, f"gen_{tag}.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"📄 Saved generated code to {script_path}")

    proc = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    out_log = log_text(f"exec_stdout_{tag}", proc.stdout or "<EMPTY>")
    err_log = log_text(f"exec_stderr_{tag}", proc.stderr or "<EMPTY>")

    if proc.stdout.strip():
        print(f"✅ Execution output saved to {out_log}")
    if proc.stderr.strip():
        print(f"⚠️ Execution errors saved to {err_log}")


# -------------------------
# Main
# -------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python nl_to_code_runner.py \"<your request>\"")
        sys.exit(1)

    user_request = sys.argv[1]

    prompt = (
        "You are a Python coding assistant.\n"
        "Respond ONLY with Python code in a fenced code block like this:\n"
        "```python\n<code here>\n```\n"
        "Do not include any explanations, notes, or text before or after the code.\n"
        f"Write Python code to: {user_request}\n"
        "The code must be self-contained and runnable.\n"
    )

    print(f"💬 Sending request to {MODEL_NAME}...")
    raw_output = call_ollama(prompt)
    if not raw_output:
        print("❌ No output from Ollama.")
        sys.exit(1)

    code = extract_first_code_block(raw_output)
    if not code.strip():
        print("❌ No code found in Ollama output.")
        sys.exit(1)

    log_text("ollama_code_clean", code)
    execute_code(code, _ts())


if __name__ == "__main__":
    main()

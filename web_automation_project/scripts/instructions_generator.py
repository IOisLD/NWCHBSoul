# scripts/instructions_generator.py

import os

def generate_instructions(filename="web_automation_project/docs/instructions.txt", instructions=None):
    """
    Save dynamic instructions to a .txt file.

    Args:
        filename (str): Output text file path.
        instructions (list of str): Each string is one step.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if instructions is None:
        instructions = [
            "Update the payment for tenants:",
            "- Use 'Receipt Amount' as new payment value",
            "- Match tenants by 'Tenant Name' or 'Property Address'",
            "- Apply updates only if 'Status' is 'Pending'"
        ]

    with open(filename, "w", encoding="utf-8") as f:
        for line in instructions:
            f.write(line + "\n")

    print(f"[INFO] Instructions saved to {filename}")


class InstructionsGenerator:
    """Simple instructions aggregator compatible with `main.py`.

    Usage:
        instructions = InstructionsGenerator(path)
        instructions.log("...message...")
        instructions.close()
    """

    def __init__(self, filename="web_automation_project/docs/instructions.txt"):
        self.filename = filename
        self._lines = []

    def log(self, line: str):
        self._lines.append(str(line))

    def close(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, "w", encoding="utf-8") as f:
            for l in self._lines:
                f.write(l + "\n")
        print(f"[INFO] Instructions saved to {self.filename}")

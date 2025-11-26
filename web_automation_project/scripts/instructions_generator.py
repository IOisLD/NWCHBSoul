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

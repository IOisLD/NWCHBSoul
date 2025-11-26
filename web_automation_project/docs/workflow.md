web_automation_project/
│
├─ input_data/
│   └─ input.xlsx           # Loaded from production (Excel/CSV/TXT)
│
├─ scripts/
│   ├─ main.py              # Main workflow orchestrator
│   ├─ load_input.py        # Dynamic loader for Excel/CSV/TXT
│   ├─ browser_manager.py   # Handles Playwright browser sessions
│   ├─ dom_actions.py       # Reads/updates web DOM dynamically
│   ├─ utils.py             # Helpers (Excel reading, logging, fuzzy matching)
│   └─ output_container.py  # Generic container for branching actions
│
├─ config/
│   └─ steps_config.json    # JSON defining dynamic actions & workflow
│
├─ results/
│   └─ output.xlsx          # Captured results or dry run outputs
│
└─ requirements.txt         # Python dependencies

# 🛰️ ORBIT — Autonomous AI Computer-Use Agent

ORBIT is a local AI agent designed to understand natural-language tasks, generate execution plans, select appropriate tools, perform file-system operations, verify results, recover from failures, and maintain execution memory.

The project combines an AI planning layer with deterministic local fallback planning, a tool execution system, safety controls, persistent memory, and a React-based monitoring dashboard.

---

## ✨ Features

### 🧠 AI Task Planning
ORBIT converts natural-language instructions into structured execution plans and machine-executable actions.

Example:

```text
Create folder D:\ORBIT_AI_AGENT\ProjectBackup,
copy D:\ORBIT_AI_AGENT\renamed_test.txt into it,
and list the files inside it
```

ORBIT converts this into:

```text
1. Create the destination folder
2. Copy the requested file
3. List the contents of the new folder
```

---

### ⚡ Local Fallback Planner

ORBIT includes a deterministic local planner for supported file-system commands.

If the external LLM reaches its quota or becomes unavailable, ORBIT can still understand and execute supported local operations without depending entirely on the cloud model.

This improves:

- reliability
- latency
- resilience
- offline/local capability for supported commands

---

## 🛠️ File-System Tools

ORBIT currently supports:

| Tool | Description |
|---|---|
| `list_files` | Lists files and folders inside a directory |
| `read_file` | Reads text-based files |
| `create_folder` | Creates a new directory |
| `move_file` | Moves a file to another location |
| `write_file` | Creates or writes content to a file |
| `copy_file` | Copies files |
| `search_files` | Searches recursively for files |
| `delete_file` | Deletes a file after confirmation |
| `rename_file` | Renames a file |
| `rename_folder` | Renames a directory |
| `delete_folder` | Deletes a folder after confirmation |
| `organize_by_type` | Organizes files based on their extensions |

---

## 🔗 Multi-Action Workflows

ORBIT can execute multiple dependent actions sequentially.

Example:

```text
Create folder D:\ORBIT_AI_AGENT\ProjectBackup,
copy D:\ORBIT_AI_AGENT\renamed_test.txt into it,
and list the files inside it
```

Execution:

```text
create_folder
      ↓
copy_file
      ↓
list_files
      ↓
verification
```

Each action is executed and verified before the workflow proceeds.

---

## 🛡️ Safety Layer

Destructive operations require explicit user confirmation.

Currently protected operations include:

```text
delete_file
delete_folder
```

ORBIT pauses execution and asks the user for confirmation before performing the destructive action.

This prevents accidental deletion of files or directories.

---

## ✅ Execution Verification

After a tool executes, ORBIT passes the result through a verifier.

The verifier determines whether the action:

- succeeded
- should proceed to the next action
- should be retried
- requires replanning
- failed because a resource does not exist
- reached the retry limit

This provides more reliable execution than simply assuming every tool call succeeded.

---

## 🔁 Error Handling and Recovery

ORBIT distinguishes between different types of failures.

Examples include:

```text
resource_not_found
permission_denied
destination_exists
invalid_path
invalid_tool_input
max_retries_reached
llm_quota_exceeded
llm_service_unavailable
```

Structural failures can be routed through ORBIT's recovery/replanning flow rather than repeatedly executing the same failed action.

---

## 🧩 Agent Architecture

ORBIT uses a modular agent architecture.

```text
                    ┌─────────────────┐
                    │    User Task    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Planner     │
                    │ AI + Local Plan │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Tool Selector  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Safety Check   │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
              Safe action      Destructive action
                    │                 │
                    │                 ▼
                    │        User Confirmation
                    │                 │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Executor     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Verifier     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
         Next Action      Completed      Recovery /
                                         Replanning
                             │
                             ▼
                    ┌─────────────────┐
                    │     Memory      │
                    └─────────────────┘
```

---

## 🧠 Persistent Memory

ORBIT stores information about previous task executions.

The dashboard exposes recent execution memory so previous tasks and their statuses can be reviewed.

Memory can also be provided to the planning layer as context when relevant.

---

## 🖥️ ORBIT Dashboard

ORBIT includes a React-based user interface for interacting with and monitoring the agent.

The dashboard provides:

- task input
- generated plan
- agent status
- user-friendly ORBIT responses
- execution trace
- tool results
- execution history
- persistent memory
- available tool viewer
- safety confirmation dialogs
- light and dark themes

---

## 🎨 Status System

The dashboard visually distinguishes execution states.

### Success

Completed tasks are displayed using the success state.

### Warning

Warnings are used for states such as:

```text
confirmation_required
llm_quota_exceeded
llm_service_unavailable
```

### Error

Errors are displayed for states such as:

```text
resource_not_found
permission_denied
invalid_path
planner_error
max_retries_reached
```

---

## 🧪 Tested Workflows

### 1. Standard File Operation

```text
List all files inside D:\ORBIT_AI_AGENT
```

Expected behavior:

```text
Plan → Tool Selection → Execution → Verification → Completed
```

---

### 2. Missing Resource

```text
Read D:\ORBIT_AI_AGENT\does_not_exist.txt
```

ORBIT detects the missing resource and returns an appropriate failure state rather than reporting a misleading LLM quota error.

---

### 3. Multi-Action Execution

```text
Create folder D:\ORBIT_AI_AGENT\FinalTest,
copy D:\ORBIT_AI_AGENT\renamed_test.txt into it,
and list the files inside it
```

Expected actions:

```text
create_folder
copy_file
list_files
```

---

### 4. Destructive Action Safety

```text
Delete folder D:\ORBIT_AI_AGENT\FinalTest
```

ORBIT pauses execution and requires explicit confirmation before deleting the directory.

---

## 💻 Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- Python-dotenv
- Google GenAI SDK

### Agent System

- Modular planning architecture
- Local deterministic planner
- Tool selection
- Tool execution
- Verification
- Recovery/replanning
- Safety layer
- Persistent memory

### Frontend

- React
- Vite
- JavaScript
- CSS

### API

ORBIT exposes a FastAPI API used by the React frontend.

Important endpoints include:

```text
POST /agent/run
POST /agent/confirm

GET /agent/history
GET /agent/memory
GET /agent/tools
```

---

# 📁 Project Structure

```text
ORBIT_AI_AGENT/
│
├── agent/
│   ├── state.py
│   ├── planner.py
│   ├── local_planner.py
│   ├── tool_selector.py
│   ├── executor.py
│   ├── verifier.py
│   ├── safety.py
│   ├── recovery.py
│   ├── replanner.py
│   └── graph.py
│
├── tools/
│   └── file_tools.py
│
├── memory/
│   └── memory_manager.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── package-lock.json
│
├── api.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

> The exact internal file structure may evolve as ORBIT is extended.

---

# 🚀 Running ORBIT Locally

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd ORBIT_AI_AGENT
```

---

## 2. Create a Python Virtual Environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 3. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_api_key_here
```

Never commit your `.env` file or API keys to GitHub.

---

## 5. Start the FastAPI Backend

From the project root:

```powershell
uvicorn api:app --reload
```

The backend normally runs at:

```text
http://127.0.0.1:8000
```

FastAPI documentation is available locally at:

```text
http://127.0.0.1:8000/docs
```

---

## 6. Start the React Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite normally starts the frontend at:

```text
http://localhost:5173
```

Open the address shown by Vite in your browser.

---

# 🧪 Example Commands

### List files

```text
List all files inside D:\ORBIT_AI_AGENT
```

### Read a file

```text
Read D:\ORBIT_AI_AGENT\notes.txt
```

### Create a folder

```text
Create folder D:\ORBIT_AI_AGENT\NewFolder
```

### Rename a file

```text
Rename D:\ORBIT_AI_AGENT\test.txt to renamed_test.txt
```

### Rename a folder

```text
Rename folder D:\ORBIT_AI_AGENT\TestFolder to RenamedFolder
```

### Delete a file

```text
Delete D:\ORBIT_AI_AGENT\test.txt
```

### Delete a folder

```text
Delete folder D:\ORBIT_AI_AGENT\TestFolder
```

### Organize files

```text
Organize all files in D:\ORBIT_AI_AGENT\DownloadsTest by file type
```

### Multi-action task

```text
Create folder D:\ORBIT_AI_AGENT\Backup,
copy D:\ORBIT_AI_AGENT\notes.txt into it,
and list the files inside it
```

---

# 🔐 Security

ORBIT can interact with the local file system, so safety is an important part of the architecture.

Current safeguards include:

- confirmation before destructive operations
- explicit destructive-tool classification
- structured tool inputs
- execution verification
- bounded retries
- controlled tool selection
- local fallback planning for supported commands

Users should still run ORBIT in a controlled environment and avoid exposing sensitive directories while experimenting with new tools.

---

# 🗺️ Future Improvements

Potential extensions include:

- richer natural-language local planning
- additional computer-use tools
- browser automation
- application launching
- document operations
- improved contextual memory
- smarter recovery strategies
- configurable permissions
- sandboxed execution
- automated test suite
- authentication for remote deployments
- containerized deployment

---

# 📸 Screenshots

Add screenshots here before publishing the repository.

Suggested screenshots:

### ORBIT Workspace

```text
screenshots/orbit-workspace.png
```

### Successful Multi-Action Execution

```text
screenshots/orbit-multi-action.png
```

### Safety Confirmation

```text
screenshots/orbit-confirmation.png
```

### Execution History

```text
screenshots/orbit-history.png
```

---

# 🎯 Project Objective

ORBIT was built to explore how an AI agent can move beyond text generation and perform structured, verifiable actions on a computer.

The project focuses on the complete agent loop:

```text
Understand
   ↓
Plan
   ↓
Select Tools
   ↓
Check Safety
   ↓
Execute
   ↓
Verify
   ↓
Recover
   ↓
Remember
```

The goal is not simply to call an LLM, but to build an agent architecture around the model that remains controlled, observable, and resilient.

---

## 👩‍💻 Author

**Sakshi Galgale**

MSc Artificial Intelligence  
Queen's University Belfast

---

## 📄 License

This project is intended for educational and portfolio purposes.

A formal open-source license can be added before public distribution.
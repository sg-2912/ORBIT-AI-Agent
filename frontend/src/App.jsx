import { useEffect, useState } from "react";
import "./App.css";


function App() {

  /* =========================================
     STATE
  ========================================= */

  const [task, setTask] = useState("");
  const [result, setResult] = useState(null);

  const [activePage, setActivePage] =
    useState("workspace");

  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] =
    useState(false);

  const [memory, setMemory] = useState([]);
  const [memoryLoading, setMemoryLoading] =
    useState(false);

  const [tools, setTools] = useState([]);
  const [toolsLoading, setToolsLoading] =
    useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [
    pendingConfirmation,
    setPendingConfirmation
  ] = useState(null);

  const [
    confirmLoading,
    setConfirmLoading
  ] = useState(false);

  const [theme, setTheme] = useState(() => {
    return (
      localStorage.getItem("orbit-theme")
      || "light"
    );
  });


  /* =========================================
     THEME
  ========================================= */

  useEffect(() => {
    document.documentElement.setAttribute(
      "data-theme",
      theme
    );

    localStorage.setItem(
      "orbit-theme",
      theme
    );
  }, [theme]);


  const toggleTheme = () => {
    setTheme(
      theme === "light"
        ? "dark"
        : "light"
    );
  };


  /* =========================================
     HELPERS
  ========================================= */

  const formatInput = (input) => {
    if (
      typeof input === "object"
      && input !== null
    ) {
      return JSON.stringify(
        input,
        null,
        2
      );
    }

    return input ?? "";
  };


  const formatStatus = (status) => {
    if (!status) {
      return "Ready";
    }

    return status
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) =>
        letter.toUpperCase()
      );
  };


  const getStatusType = (status) => {
    if (!status) {
      return "neutral";
    }

    if (status === "completed") {
      return "success";
    }

    if (
      status === "confirmation_required"
      || status === "destination_exists"
      || status === "llm_quota_exceeded"
      || status === "llm_service_unavailable"
      || status === "cancelled"
    ) {
      return "warning";
    }

    if (
      status === "resource_not_found"
      || status === "permission_denied"
      || status === "invalid_path"
      || status === "invalid_tool_input"
      || status === "unsupported_tool"
      || status === "planner_error"
      || status === "llm_error"
      || status === "max_retries_reached"
    ) {
      return "error";
    }

    return "neutral";
  };


  const getStatusIcon = (status) => {
    const type = getStatusType(status);

    if (type === "success") {
      return "✓";
    }

    if (type === "warning") {
      return "!";
    }

    if (type === "error") {
      return "×";
    }

    return "◉";
  };


  const getConfirmationTarget = () => {
    if (!pendingConfirmation?.tool_input) {
      return "";
    }

    const input =
      pendingConfirmation.tool_input;

    if (typeof input === "string") {
      return input;
    }

    return (
      input.file_path
      || input.folder_path
      || input.source_path
      || input.destination_path
      || "Unknown target"
    );
  };


  const openWorkspace = () => {
    setActivePage("workspace");
    setError("");
  };


  /* =========================================
     RUN AGENT
  ========================================= */

  const runAgent = async () => {
    if (!task.trim()) {
      setError(
        "Please enter a task."
      );
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setPendingConfirmation(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/agent/run",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body: JSON.stringify({
            task
          })
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail
          || "Something went wrong."
        );
      }

      setResult(data);

      if (data.requires_confirmation) {
        setPendingConfirmation({
          task: data.task,
          selected_tool:
            data.selected_tool,
          tool_input:
            data.tool_input
        });
      }

    } catch (err) {
      setError(
        err.message
        || "Unable to run ORBIT."
      );

    } finally {
      setLoading(false);
    }
  };


  /* =========================================
     CONFIRM ACTION
  ========================================= */

  const confirmAction = async () => {
    if (!pendingConfirmation) {
      return;
    }

    setConfirmLoading(true);
    setError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/agent/confirm",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body: JSON.stringify({
            task:
              pendingConfirmation.task,

            selected_tool:
              pendingConfirmation.selected_tool,

            tool_input:
              pendingConfirmation.tool_input
          })
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail
          || "Could not confirm the action."
        );
      }

      setResult((previous) => ({
        ...previous,

        status:
          data.status,

        message:
          data.message,

        history:
          data.history || [],

        tool_result:
          data.tool_result,

        requires_confirmation:
          false
      }));

      setPendingConfirmation(null);

    } catch (err) {
      setError(
        err.message
        || "Unable to confirm action."
      );

    } finally {
      setConfirmLoading(false);
    }
  };


  /* =========================================
     CANCEL CONFIRMATION
  ========================================= */

  const cancelConfirmation = () => {
    setPendingConfirmation(null);

    setResult((previous) => {
      if (!previous) {
        return previous;
      }

      return {
        ...previous,

        status:
          "cancelled",

        message:
          "The action was cancelled. "
          + "No destructive operation "
          + "was performed.",

        requires_confirmation:
          false
      };
    });
  };


  /* =========================================
     LOAD HISTORY
  ========================================= */

  const loadHistory = async () => {
    setActivePage("history");
    setHistoryLoading(true);
    setError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/agent/history"
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail
          || "Could not load execution history."
        );
      }

      setHistory(
        data.tasks || []
      );

    } catch (err) {
      setError(
        err.message
      );

    } finally {
      setHistoryLoading(false);
    }
  };


  /* =========================================
     LOAD MEMORY
  ========================================= */

  const loadMemory = async () => {
    setActivePage("memory");
    setMemoryLoading(true);
    setError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/agent/memory"
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail
          || "Could not load memory."
        );
      }

      setMemory(
        data.memory || []
      );

    } catch (err) {
      setError(
        err.message
      );

    } finally {
      setMemoryLoading(false);
    }
  };


  /* =========================================
     LOAD TOOLS
  ========================================= */

  const loadTools = async () => {
    setActivePage("tools");
    setToolsLoading(true);
    setError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/agent/tools"
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail
          || "Could not load tools."
        );
      }

      setTools(
        data.tools || []
      );

    } catch (err) {
      setError(
        err.message
      );

    } finally {
      setToolsLoading(false);
    }
  };


  /* =========================================
     THEME BUTTON
  ========================================= */

  const ThemeButton = () => (
    <button
      className="theme-toggle"
      onClick={toggleTheme}
      title="Toggle theme"
    >
      {theme === "light"
        ? "☾"
        : "☀"}
    </button>
  );


  /* =========================================
     JSX
  ========================================= */

  return (
    <div className="app">

      {/* =====================================
          SIDEBAR
      ===================================== */}

      <aside className="sidebar">

        <div className="logo">

          <div className="logo-icon">
            O
          </div>

          <div>
            <h2>ORBIT</h2>
            <span>AI AGENT</span>
          </div>

        </div>


        <nav>

          <button
            className={
              `nav-item ${
                activePage === "workspace"
                  ? "active"
                  : ""
              }`
            }
            onClick={openWorkspace}
          >
            <span>◈</span>
            Agent Workspace
          </button>


          <button
            className={
              `nav-item ${
                activePage === "history"
                  ? "active"
                  : ""
              }`
            }
            onClick={loadHistory}
          >
            <span>◷</span>
            Execution History
          </button>


          <button
            className={
              `nav-item ${
                activePage === "memory"
                  ? "active"
                  : ""
              }`
            }
            onClick={loadMemory}
          >
            <span>▱</span>
            Memory
          </button>


          <button
            className={
              `nav-item ${
                activePage === "tools"
                  ? "active"
                  : ""
              }`
            }
            onClick={loadTools}
          >
            <span>⌘</span>
            Tools
          </button>

        </nav>


        <div className="sidebar-decoration">
          <div className="orbit-circle one" />
          <div className="orbit-circle two" />
          <div className="orbit-circle three" />
        </div>


        <div className="agent-status">

          <span className="status-dot" />

          <div>
            <strong>
              ORBIT Online
            </strong>

            <p>
              Agent ready
            </p>
          </div>

        </div>

      </aside>


      {/* =====================================
          MAIN
      ===================================== */}

      <main className="main-content">


        {/* =====================================
            WORKSPACE
        ===================================== */}

        {activePage === "workspace" && (
          <>

            <header className="top-header">

              <div>

                <p className="eyebrow">
                  AUTONOMOUS WORKSPACE
                </p>

                <h1>
                  What should{" "}
                  <span className="orbit-heading">
                    ORBIT
                  </span>{" "}
                  do?
                </h1>

                <p className="subtitle">
                  Give your AI agent a task.
                  ORBIT will plan, select tools,
                  execute actions and verify
                  the result.
                </p>

              </div>

              <ThemeButton />

            </header>


            {/* TASK */}

            <section className="task-card">

              <textarea
                placeholder={
                  "Ask ORBIT to perform a task..."
                }
                value={task}
                onChange={(event) =>
                  setTask(
                    event.target.value
                  )
                }
              />


              {error && (
                <p className="error-message">
                  {error}
                </p>
              )}


              <div className="task-footer">

                <div className="capabilities">

                  <span className="chip planner">
                    ◇ Planner
                  </span>

                  <span className="chip tools">
                    ⑂ Tools
                  </span>

                  <span className="chip memory">
                    ▱ Memory
                  </span>

                  <span className="chip verify">
                    ◉ Verification
                  </span>

                </div>


                <button
                  className="run-button"
                  onClick={runAgent}
                  disabled={loading}
                >
                  {loading
                    ? "Running..."
                    : "Run Agent →"}
                </button>

              </div>

            </section>


            {/* ORBIT RESPONSE */}

            {result?.message && (
              <section
                className={
                  `agent-response-card ${
                    getStatusType(
                      result.status
                    )
                  }`
                }
              >

                <div className="agent-response-icon">
                  {getStatusIcon(
                    result.status
                  )}
                </div>


                <div className="agent-response-content">

                  <span className="agent-response-label">
                    ORBIT RESPONSE
                  </span>

                  <p>
                    {result.message}
                  </p>

                </div>

              </section>
            )}


            {/* PLAN + STATUS */}

            <section className="dashboard-grid">


              {/* PLAN */}

              <div className="panel plan-panel">

                <div className="panel-header">

                  <div className="panel-title">

                    <div className="panel-icon">
                      ≡
                    </div>

                    <span>
                      PLAN
                    </span>

                  </div>


                  <span
                    className={
                      `status-badge ${
                        getStatusType(
                          result?.status
                        )
                      }`
                    }
                  >
                    {result
                      ? formatStatus(
                          result.status
                        )
                      : "Waiting"}
                  </span>

                </div>


                {!result ? (

                  <p className="empty-state">
                    ORBIT's generated execution
                    plan will appear here.
                  </p>

                ) : result.plan?.length > 0 ? (

                  <div className="plan-list">

                    {result.plan.map(
                      (step, index) => (

                        <div
                          className="plan-step"
                          key={index}
                        >

                          <span className="step-number">
                            {index + 1}
                          </span>

                          <p>
                            {step}
                          </p>

                        </div>

                      )
                    )}

                  </div>

                ) : (

                  <p className="empty-state">
                    No executable plan was generated.
                  </p>

                )}

              </div>


              {/* STATUS */}

              <div className="panel status-panel">

                <div className="panel-header">

                  <div className="panel-title">

                    <div className="panel-icon">
                      ⌁
                    </div>

                    <span>
                      AGENT STATUS
                    </span>

                  </div>

                </div>


                <div className="status-content">

                  <div
                    className={
                      `status-ring ${
                        loading
                          ? "working"
                          : getStatusType(
                              result?.status
                            )
                      }`
                    }
                  >
                    <span>
                      {loading
                        ? "…"
                        : result
                          ? getStatusIcon(
                              result.status
                            )
                          : "◉"}
                    </span>
                  </div>


                  <div>

                    <h3>
                      {loading
                        ? "Running"
                        : result
                          ? formatStatus(
                              result.status
                            )
                          : "Ready"}
                    </h3>


                    <p>
                      {loading
                        ? "Executing your task..."

                        : result?.status
                          ===
                          "confirmation_required"

                          ? "Waiting for your confirmation"

                          : result?.status
                            === "completed"

                            ? "Task completed successfully"

                            : result

                              ? result.message
                                || "Task execution finished"

                              : "Waiting for a task"}
                    </p>

                  </div>

                </div>

              </div>

            </section>


            {/* EXECUTION TRACE */}

            <section className="panel execution-panel">

              <div className="panel-header">

                <div className="panel-title">

                  <div className="panel-icon">
                    &gt;_
                  </div>

                  <span>
                    EXECUTION TRACE
                  </span>

                </div>


                <span className="action-count">
                  {result
                    ? `${
                        result.history?.length
                        || 0
                      } actions`
                    : "0 actions"}
                </span>

              </div>


              {!result?.history?.length ? (

                <p className="empty-state">
                  Tool calls and verification
                  results will appear here.
                </p>

              ) : (

                <div className="execution-list">

                  {result.history.map(
                    (item, index) => (

                      <div
                        className="trace-row"
                        key={index}
                      >

                        <div className="timeline">

                          <div
                            className={
                              `timeline-circle ${
                                item.result?.success
                                  ? "success"
                                  : "error"
                              }`
                            }
                          >
                            {index + 1}
                          </div>


                          {index
                            <
                            result.history.length - 1
                            && (
                            <div
                              className="timeline-line"
                            />
                          )}

                        </div>


                        <div className="execution-item">

                          <div className="execution-top">

                            <strong>
                              Action{" "}
                              {item.action_number}
                            </strong>

                            <span className="tool-badge">
                              {item.tool}
                            </span>

                          </div>


                          <div className="execution-details">

                            <div>

                              <span className="detail-label">
                                Input
                              </span>

                              <p>
                                {formatInput(
                                  item.input
                                )}
                              </p>

                            </div>


                            <div
                              className={
                                item.result?.success
                                  ? "result-box success"
                                  : "result-box failed"
                              }
                            >

                              <span className="detail-label">
                                Result
                              </span>

                              <p>
                                {item.result?.success
                                  ? "✓ Success"
                                  : `✕ ${
                                      item.result?.error
                                      || "Failed"
                                    }`}
                              </p>

                            </div>

                          </div>

                        </div>

                      </div>

                    )
                  )}

                </div>

              )}

            </section>

          </>
        )}


        {/* =====================================
            HISTORY
        ===================================== */}

        {activePage === "history" && (

          <section className="history-page">

            <div className="history-header">

              <div>

                <p className="eyebrow">
                  EXECUTION HISTORY
                </p>

                <h1>
                  Previous{" "}
                  <span className="orbit-heading">
                    ORBIT
                  </span>{" "}
                  runs
                </h1>

                <p className="subtitle">
                  Review tasks ORBIT has executed,
                  including the tools used and
                  their results.
                </p>

              </div>

              <ThemeButton />

            </div>


            {error && (
              <p className="error-message">
                {error}
              </p>
            )}


            {historyLoading ? (

              <div className="panel">
                <p className="empty-state">
                  Loading execution history...
                </p>
              </div>

            ) : history.length === 0 ? (

              <div className="panel">
                <p className="empty-state">
                  No previous ORBIT executions found.
                </p>
              </div>

            ) : (

              <div className="history-list">

                {[...history]
                  .reverse()
                  .map(
                    (item, index) => (

                    <div
                      className="history-card"
                      key={index}
                    >

                      <div className="history-card-top">

                        <div>

                          <span className="history-number">
                            {history.length - index}
                          </span>

                          <span
                            className={
                              `history-status ${
                                getStatusType(
                                  item.status
                                )
                              }`
                            }
                          >
                            {formatStatus(
                              item.status
                            )}
                          </span>

                        </div>


                        <span className="history-actions-count">
                          {item.history?.length || 0}{" "}
                          actions
                        </span>

                      </div>


                      <h3>
                        {item.task}
                      </h3>


                      <div className="history-tools">

                        {item.history?.map(
                          (
                            action,
                            actionIndex
                          ) => (

                          <span
                            className="tool-badge"
                            key={actionIndex}
                          >
                            {action.tool}
                          </span>

                        ))}

                      </div>


                      <div className="history-details">

                        {item.history?.map(
                          (
                            action,
                            actionIndex
                          ) => (

                          <div
                            className="history-action"
                            key={actionIndex}
                          >

                            <div>

                              <strong>
                                Action{" "}
                                {action.action_number}
                              </strong>

                              <span>
                                {action.tool}
                              </span>

                            </div>


                            <p>
                              <strong>
                                Input:
                              </strong>{" "}
                              {formatInput(
                                action.input
                              )}
                            </p>


                            <p
                              className={
                                action.result?.success
                                  ? "history-success"
                                  : "history-failed"
                              }
                            >
                              {action.result?.success
                                ? "✓ Success"
                                : `✕ ${
                                    action.result?.error
                                    || "Failed"
                                  }`}
                            </p>

                          </div>

                        ))}

                      </div>

                    </div>

                  ))}

              </div>

            )}

          </section>

        )}


        {/* =====================================
            MEMORY
        ===================================== */}

        {activePage === "memory" && (

          <section className="memory-page">

            <div className="history-header">

              <div>

                <p className="eyebrow">
                  AGENT MEMORY
                </p>

                <h1>
                  What{" "}
                  <span className="orbit-heading">
                    ORBIT
                  </span>{" "}
                  remembers
                </h1>

                <p className="subtitle">
                  Review recent tasks stored
                  in ORBIT's persistent memory.
                </p>

              </div>

              <ThemeButton />

            </div>


            {error && (
              <p className="error-message">
                {error}
              </p>
            )}


            {memoryLoading ? (

              <div className="panel">
                <p className="empty-state">
                  Loading ORBIT memory...
                </p>
              </div>

            ) : memory.length === 0 ? (

              <div className="panel">
                <p className="empty-state">
                  ORBIT has no stored memory yet.
                </p>
              </div>

            ) : (

              <div className="memory-grid">

                {[...memory]
                  .reverse()
                  .map(
                    (item, index) => (

                    <div
                      className="memory-card"
                      key={index}
                    >

                      <div className="memory-icon">
                        ▱
                      </div>


                      <div className="memory-content">

                        <span className="memory-label">
                          STORED TASK
                        </span>

                        <h3>
                          {item.task}
                        </h3>


                        <span
                          className={
                            `memory-status ${
                              getStatusType(
                                item.status
                              )
                            }`
                          }
                        >
                          {formatStatus(
                            item.status
                          )}
                        </span>

                      </div>

                    </div>

                  ))}

              </div>

            )}

          </section>

        )}


        {/* =====================================
            TOOLS
        ===================================== */}

        {activePage === "tools" && (

          <section className="tools-page">

            <div className="history-header">

              <div>

                <p className="eyebrow">
                  TOOL SYSTEM
                </p>

                <h1>
                  ORBIT's{" "}
                  <span className="orbit-heading">
                    capabilities
                  </span>
                </h1>

                <p className="subtitle">
                  Explore the tools ORBIT can
                  currently use to interact
                  with your computer.
                </p>

              </div>

              <ThemeButton />

            </div>


            {error && (
              <p className="error-message">
                {error}
              </p>
            )}


            {toolsLoading ? (

              <div className="panel">
                <p className="empty-state">
                  Loading ORBIT tools...
                </p>
              </div>

            ) : tools.length === 0 ? (

              <div className="panel">
                <p className="empty-state">
                  No tools available.
                </p>
              </div>

            ) : (

              <div className="tools-grid">

                {tools.map(
                  (tool, index) => (

                  <div
                    className="tool-card"
                    key={index}
                  >

                    <div className="tool-card-icon">
                      ⌘
                    </div>


                    <div className="tool-card-content">

                      <span className="tool-type">
                        AVAILABLE TOOL
                      </span>

                      <h3>
                        {tool.name}
                      </h3>

                      <p>
                        {tool.description}
                      </p>


                      <div className="tool-input-box">

                        <span>
                          INPUT
                        </span>

                        <code>
                          {tool.input}
                        </code>

                      </div>

                    </div>

                  </div>

                ))}

              </div>

            )}

          </section>

        )}


        {/* =====================================
            FOOTER
        ===================================== */}

        <footer className="orbit-footer">
          <p>
            Designed &amp; Built by{" "}
            <strong>Sakshi Galgale</strong>
            <span className="footer-dot">•</span>
            ORBIT AI Agent
          </p>
        </footer>

      </main>


      {/* =====================================
          SAFETY CONFIRMATION
      ===================================== */}

      {pendingConfirmation && (

        <div className="confirmation-overlay">

          <div className="confirmation-modal">

            <div className="confirmation-icon">
              !
            </div>

            <p className="eyebrow">
              SAFETY CHECK
            </p>

            <h2>
              Confirmation Required
            </h2>


            <p className="confirmation-text">
              ORBIT is requesting permission
              to perform a destructive action.
            </p>


            <div className="confirmation-action">

              <span>
                ACTION
              </span>

              <strong>
                {
                  pendingConfirmation
                    .selected_tool
                }
              </strong>

            </div>


            <div className="confirmation-path">

              <span>
                TARGET
              </span>

              <code>
                {getConfirmationTarget()}
              </code>

            </div>


            <p className="confirmation-warning">
              This action cannot be undone.
            </p>


            <div className="confirmation-buttons">

              <button
                className="cancel-button"
                onClick={
                  cancelConfirmation
                }
                disabled={
                  confirmLoading
                }
              >
                Cancel
              </button>


              <button
                className="confirm-delete-button"
                onClick={
                  confirmAction
                }
                disabled={
                  confirmLoading
                }
              >
                {confirmLoading
                  ? "Processing..."
                  : "Confirm Action"}
              </button>

            </div>

          </div>

        </div>

      )}

    </div>
  );
}


export default App;
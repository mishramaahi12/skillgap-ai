import React, { useEffect, useState } from "react";

function Assessment() {
  const [tasks, setTasks] = useState([]);
  const [currentTaskIndex, setCurrentTaskIndex] = useState(0);

  const [code, setCode] = useState("");
  const [attempts, setAttempts] = useState(0);
  const [runs, setRuns] = useState(0);
  const [hintsUsed, setHintsUsed] = useState(0);
  const [timeTaken, setTimeTaken] = useState(0);

  const [result, setResult] = useState("");
  const [testResults, setTestResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [assessmentComplete, setAssessmentComplete] = useState(false);

  // Load tasks
  useEffect(() => {
    const loadTasks = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/tasks");
        const data = await response.json();

        setTasks(data.tasks || []);
        setLoading(false);
      } catch (error) {
        console.error("Could not load tasks:", error);
        setResult("Could not connect to backend.");
        setLoading(false);
      }
    };

    loadTasks();
  }, []);

  // Start timer
  useEffect(() => {
    if (loading || assessmentComplete) {
      return;
    }

    const timer = setInterval(() => {
      setTimeTaken((previousTime) => previousTime + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [loading, assessmentComplete]);

  // Record task started
  useEffect(() => {
    if (loading || tasks.length === 0 || assessmentComplete) {
      return;
    }

    const currentTask = tasks[currentTaskIndex];

    const startTask = async () => {
      try {
        await fetch("http://127.0.0.1:8000/task-start", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            user_id: "demo_user",
            task_id: currentTask.task_id
          })
        });

        console.log("Task started:", currentTask.task_id);
      } catch (error) {
        console.error("Could not record task start:", error);
      }
    };

    startTask();
  }, [loading, tasks, currentTaskIndex, assessmentComplete]);

  if (loading) {
    return (
      <div className="assessment-page">
        <div className="assessment-header">
          <div className="logo">
            SkillGap<span>AI</span>
          </div>
        </div>

        <main className="assessment-container">
          <h1>Loading assessment...</h1>
        </main>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="assessment-page">
        <main className="assessment-container">
          <h1>No assessment tasks found.</h1>
        </main>
      </div>
    );
  }

  if (assessmentComplete) {
    return (
      <div className="assessment-page">
        <div className="assessment-header">
          <div className="logo">
            SkillGap<span>AI</span>
          </div>
        </div>

        <main className="assessment-container">
          <p className="task-label">ASSESSMENT COMPLETE</p>

          <h1>Great work! 🎉</h1>

          <p className="task-description">
            You have completed all {tasks.length} assessment tasks.
            Your behavioural data has been collected for skill analysis.
          </p>

          <div className="assessment-stats">
            <div>
              <span>TASKS</span>
              <strong>{tasks.length}</strong>
            </div>

            <div>
              <span>TIME</span>
              <strong>{formatTime(timeTaken)}</strong>
            </div>
          </div>
        </main>
      </div>
    );
  }

  const currentTask = tasks[currentTaskIndex];

  // Run code
  const handleRun = async () => {
    const newRuns = runs + 1;
    const newAttempts = attempts + 1;

    setRuns(newRuns);
    setAttempts(newAttempts);

    try {
      const response = await fetch("http://127.0.0.1:8000/run", {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({
          code: code,
          user_id: "demo_user",
          task_id: currentTask.task_id,
          time_taken: timeTaken,
          runs: newRuns,
          attempts: newAttempts,
          hints_used: hintsUsed
        })
      });

      const data = await response.json();

      setTestResults(data.results || []);

      const passed = data.passed || 0;
      const total = data.total || 0;

      setResult(
        `${data.message} ${passed}/${total} test cases passed.`
      );

    } catch (error) {
      console.error("Backend error:", error);
      setResult("Could not connect to backend.");
    }
  };

  // Go to next task
  const handleNextTask = () => {
    if (currentTaskIndex === tasks.length - 1) {
      setAssessmentComplete(true);
      return;
    }

    const nextIndex = currentTaskIndex + 1;

    setCurrentTaskIndex(nextIndex);

    setCode("");
    setAttempts(0);
    setRuns(0);
    setHintsUsed(0);
    setTimeTaken(0);
    setResult("");
    setTestResults([]);
  };

  // Use hint
  const handleHint = async () => {
    const newHintsUsed = hintsUsed + 1;

    setHintsUsed(newHintsUsed);

    try {
      await fetch("http://127.0.0.1:8000/hint", {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({
          user_id: "demo_user",
          task_id: currentTask.task_id,
          time_taken: timeTaken,
          hints_used: newHintsUsed
        })
      });

      console.log("Hint usage recorded:", currentTask.task_id);

    } catch (error) {
      console.error("Could not record hint usage:", error);
    }

    alert(
      "Hint: Think about what the function should do step by step."
    );
  };

  function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);

    const remainingSeconds = seconds % 60;

    return `${minutes}:${remainingSeconds
      .toString()
      .padStart(2, "0")}`;
  }

  return (
    <div className="assessment-page">

      <div className="assessment-header">

        <div className="logo">
          SkillGap<span>AI</span>
        </div>

        <div className="progress-text">
          Assessment {currentTaskIndex + 1} of {tasks.length}
        </div>

      </div>

      <main className="assessment-container">

        <p className="task-label">
          {currentTask.skill
            .replace("_", " ")
            .toUpperCase()} TASK
        </p>

        <h1>{currentTask.title}</h1>

        <p className="task-description">
          {currentTask.description}
        </p>

        <div className="code-box">

          <div className="code-top">

            <span>{currentTask.language}</span>

            <span>
              Task #{String(currentTaskIndex + 1).padStart(2, "0")}
            </span>

          </div>

          <pre>{currentTask.starter_code}</pre>

        </div>

        <div className="answer-box">

          <label>Your solution</label>

          <textarea
            value={code}
            onChange={(event) => setCode(event.target.value)}
            placeholder="Write your solution here..."
          />

        </div>

        {result && (
          <div className="result-box">
            {result}
          </div>
        )}

        {testResults.length > 0 && (

          <div className="test-results">

            <h3>Test Results</h3>

            {testResults.map((test, index) => (

              <div
                className="test-case"
                key={index}
              >

                <div>

                  <strong>
                    Test Case {index + 1}
                  </strong>

                  <span>
                    Input: {test.input}
                  </span>

                </div>

                <span
                  className={
                    test.status === "passed"
                      ? "test-passed"
                      : "test-failed"
                  }
                >

                  {test.status === "passed"
                    ? "✓ Passed"
                    : "✗ Failed"}

                </span>

              </div>

            ))}

          </div>

        )}

        <div className="assessment-stats">

          <div>
            <span>TIME</span>
            <strong>{formatTime(timeTaken)}</strong>
          </div>

          <div>
            <span>RUNS</span>
            <strong>{runs}</strong>
          </div>

          <div>
            <span>ATTEMPTS</span>
            <strong>{attempts}</strong>
          </div>

          <div>
            <span>HINTS</span>
            <strong>{hintsUsed}</strong>
          </div>

        </div>

        <div className="assessment-actions">

          <button
            className="hint-btn"
            onClick={handleHint}
          >
            Need a hint?
          </button>

          <button
            className="submit-btn"
            onClick={handleRun}
          >
            Run & Submit →
          </button>

          {result &&
            result.includes("All test cases passed!") && (

              <button
                className="submit-btn"
                onClick={handleNextTask}
              >
                {currentTaskIndex === tasks.length - 1
                  ? "Finish Assessment →"
                  : "Next Task →"}
              </button>

            )}

        </div>

      </main>

    </div>
  );
}

export default Assessment;
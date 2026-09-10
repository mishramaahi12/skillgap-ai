import React from "react";
import "./App.css";
import Assessment from "./Assessment";

function App() {
  const [showAssessment, setShowAssessment] = React.useState(false);

  if (showAssessment) {
    return <Assessment />;
  }

  return (
    <div className="app">
      <nav className="navbar">
        <div className="logo">
          SkillGap<span>AI</span>
        </div>

        <div className="nav-links">
          <a href="#how-it-works">How it works</a>
          <a href="#skills">Skills</a>
          <button className="login-btn">Log in</button>
        </div>
      </nav>

      <main className="hero">
        <div className="badge">
          ✦ AI-powered skill assessment
        </div>

        <h1>
          Discover your
          <br />
          <span>real skill gaps.</span>
        </h1>

        <p className="hero-text">
          SkillGap AI analyzes how you actually solve problems —
          not just what certificates you have.
        </p>

        <div className="hero-buttons">
         <button
         className="primary-btn"
          onClick={() => setShowAssessment(true)}
        >
           Start Assessment →
          </button>

          <button className="secondary-btn">
            See how it works
          </button>
        </div>

        <div className="skill-preview" id="skills">
          <div className="preview-header">
            <div>
              <p className="small-label">YOUR SKILL PROFILE</p>
              <h2>Initial assessment</h2>
            </div>

            <div className="score">
              <strong>68%</strong>
              <span>overall</span>
            </div>
          </div>

          <div className="skills">
            <Skill name="Debugging" score={42} />
            <Skill name="Problem Decomposition" score={61} />
            <Skill name="Code Quality" score={73} />
          </div>
        </div>
      </main>

      <section className="how-section" id="how-it-works">
        <p className="small-label">HOW IT WORKS</p>
        <h2>
          We analyze <span>how you think.</span>
        </h2>

        <div className="steps">
          <div className="step">
            <div className="step-number">01</div>
            <h3>Assess</h3>
            <p>
              Solve real-world coding and problem-solving tasks.
            </p>
          </div>

          <div className="step">
            <div className="step-number">02</div>
            <h3>Diagnose</h3>
            <p>
              We analyze your attempts, errors, time and behavior.
            </p>
          </div>

          <div className="step">
            <div className="step-number">03</div>
            <h3>Improve</h3>
            <p>
              Get a personalized practice roadmap for your weak areas.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

function Skill({ name, score }) {
  return (
    <div className="skill">
      <div className="skill-info">
        <span>{name}</span>
        <strong>{score}%</strong>
      </div>

      <div className="progress">
        <div
          className="progress-fill"
          style={{ width: `${score}%` }}
        ></div>
      </div>
    </div>
  );
}

export default App;
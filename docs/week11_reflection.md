# 🧠 Capstone Planning Document

---

## 🔖 Section 0: Fellow Details

| Field                  | Your Entry             |
|------------------------|------------------------|
| Name                   | Abil Girma Teshome     |
| GitHub Username        | AGT-tech               |
| Preferred Feature Track| Smart                  |
| Team Interest          | Yes — Contributor      |


---

## ✍️ Section 1: Week 11 Reflection

### **Key Takeaways**
- Capstone projects should be scoped realistically and focused on demonstrating growth.
- Expectation is to showcase problem-solving and full-stack thinking.
- Working iteratively is better than trying to finish everything at once.
- Documenting design decisions is crucial.
- Stretch goals should challenge but not overwhelm.

### **Concept Connections**
- **Strongest:** API integrations, importing,  basic GUI with Tkinter.
- **Needs Practice:** Error handling across modules, unit testing, structuring larger codebases, Algorithmic Thinking.

### **Early Challenges**
- Creating files and folders and forgeting to commit them immediatly.
- Confusion around proper folder setup for feature separation.
- Wanting to ruch, but also realizing starting slow and understanding everything is a way to go

### **Support Strategies**
- Attend Tuesday office hours for code reviews.
- Use canvas to reach out to someone who can post my question in the  `#capstone-questions` for debugging setup issues.
- Rewatch the Week 1 session on error handling, and week 3 on Algorithimic thinking.

---

## 🧠 Section 2: Feature Selection Rationale

| #  | Feature Name       | Difficulty (1–3)     | Why You Chose It / Learning Goal                          |
|----|--------------------|----------------------|------------------------------------------------------------|
| 1  | Simple Statistics  | 1                    | To track min/max temperatures and count weather types      |
| 2  | Theme Switcher     | 2                    | To give users the option to switch themes and retain them  |
| 3  | Trend Detection     | 3                    | To make the service simple through insights and patterns    |
| –  | Achievement System | **Enhancement**      | To challenge and excite users to engage with the app       |


> 🧩 Tip used: Feature 3 is a Level 3 challenge to push smart functionality.

---

## 🗂️ Section 3: High-Level Architecture Sketch

**Core Structure:**

![Architecture Sketch: for the core structure](../screenshots/architecture_sketch.png)

**Data Flow:**

User Input → Weather API → Processed Results → Suggestion Engine → Display/UI → Logs Stored

---

## 📊 Section 4: Data Model Plan

| File/Table Name       | Format | Example Row / Structure                                               |
| --------------------- | ------ | --------------------------------------------------------------------- |
| `weather_log.csv`     | CSV    | `2025-06-26,72,Fair` — Date, temperature, condition                   |
| `user_settings.json`  | JSON   | `{"theme": "dark", "font_size": 14}`                                  |
| `trends_summary.json` | JSON   | `{"hot_days": 12, "cold_days": 4, "most_common": "Sunny"}`            |
| `achievements.csv`    | CSV    | `2025-06-26,Checked Weather,True` — Date, Achievement Name, Completed |

---

## 📆 Section 5: Personal Project Timeline (Weeks 12–17)

| Week | Monday         | Tuesday       | Wednesday     | Thursday      | Key Milestone         |
|------|----------------|---------------|----------------|----------------|------------------------|
| 12   | API setup      | Error handling| Tkinter shell | Buffer day    | Basic working app      |
| 13   | Feature 1      | –             | –             | Integrate     | Feature 1 complete     |
| 14   | Feature 2 start| –             | Review & test | Finish        | Feature 2 complete     |
| 15   | Feature 3      | Polish UI     | Error passing | Refactor      | All features complete  |
| 16   | Enhancement    | Docs          | Tests         | Packaging     | Ready-to-ship app      |
| 17   | Rehearse       | Buffer        | Showcase      | –             | Demo Day               |

---

## ⚠️ Section 6: Risk Assessment

| Risk               | Likelihood | Impact | Mitigation Plan                          |
|--------------------|------------|--------|-------------------------------------------|
| API Rate Limit     | Medium     | Medium | Add delays or cache recent results        |
| Feature Overload   | High       | High   | Prioritize core features; enhancement is optional |
| Tkinter Bugs       | Medium     | Medium | Build incrementally and test small units  |

---

## 🤝 Section 7: Support Requests

- Help testing API response parsing with edge cases.
- Guidance on modular Tkinter design.
- Best practices for data logging (text vs CSV).
- Feedback on enhancement (is voice input feasible in timeframe?).
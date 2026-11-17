const visitorKey = "figure-skating-visitor";
const localHost = ["localhost", "127.0.0.1"].includes(location.hostname);
const apiBase = localHost && location.port !== "8000" ? "http://localhost:8000" : "";
let visitorId = localStorage.getItem(visitorKey);
if (!visitorId) {
  visitorId = Array.from(crypto.getRandomValues(new Uint8Array(16)), byte => byte.toString(16).padStart(2, "0")).join("");
  localStorage.setItem(visitorKey, visitorId);
}

const form = document.querySelector("#quiz-form");
const questionsBox = document.querySelector("#questions");
const statusBox = document.querySelector("#quiz-status");
const resultBox = document.querySelector("#result");
const historyList = document.querySelector("#history-list");
let questions = [];

async function loadHistory() {
  const response = await fetch(`${apiBase}/api/attempts?visitor_id=${visitorId}`);
  if (!response.ok) throw new Error("Could not load your history");
  const attempts = await response.json();
  historyList.replaceChildren();
  if (!attempts.length) {
    const item = document.createElement("li");
    item.textContent = "No attempts yet";
    historyList.append(item);
    return;
  }
  for (const attempt of attempts) {
    const item = document.createElement("li");
    const date = new Date(`${attempt.created_at}Z`).toLocaleString("en-GB");
    item.textContent = `${date} · ${attempt.score}/${attempt.total} correct`;
    historyList.append(item);
  }
}

async function loadQuestions() {
  const response = await fetch(`${apiBase}/api/questions`);
  if (!response.ok) throw new Error("Could not load the questions");
  questions = await response.json();
  statusBox.textContent = "Choose an answer for each question, then submit.";
  for (const [index, question] of questions.entries()) {
    const fieldset = document.createElement("fieldset");
    const legend = document.createElement("legend");
    legend.textContent = `${String(index + 1).padStart(2, "0")}  ${question.question}`;
    fieldset.append(legend);
    question.choices.forEach((choice, choiceIndex) => {
      const label = document.createElement("label");
      const input = document.createElement("input");
      input.type = "radio";
      input.name = `question-${question.id}`;
      input.value = choiceIndex;
      label.append(input, document.createTextNode(choice));
      fieldset.append(label);
    });
    questionsBox.append(fieldset);
  }
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  const answers = questions.map(question => {
    const selected = form.querySelector(`input[name="question-${question.id}"]:checked`);
    return selected ? Number(selected.value) : null;
  });
  if (answers.includes(null)) {
    statusBox.textContent = "Please answer every question first.";
    return;
  }
  const button = form.querySelector("button");
  button.disabled = true;
  try {
    const response = await fetch(`${apiBase}/api/attempts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ visitor_id: visitorId, answers }),
    });
    if (!response.ok) throw new Error("Submission failed. Please try again.");
    const result = await response.json();
    resultBox.textContent = `You got ${result.score} out of ${result.total} correct!`;
    resultBox.hidden = false;
    statusBox.textContent = "Your result has been saved.";
    await loadHistory();
  } catch (error) {
    statusBox.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

Promise.all([loadQuestions(), loadHistory()]).catch(() => {
  statusBox.textContent = "Could not reach the API. Please check that the Python server is running.";
});

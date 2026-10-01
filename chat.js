// ============================================
// CONFIG — points to YOUR Flask backend (no paid API!)
// ============================================
const BACKEND_URL = 'http://127.0.0.1:5000';

// ---------- Grab chat elements ----------
const chatWindow = document.getElementById('chatWindow');
const chatInput  = document.getElementById('chatInput');
const sendBtn    = document.getElementById('sendBtn');

// ---------- Add a message bubble to the chat window ----------
function addMessage(text, sender) {
  const row = document.createElement('div');
  row.className = `msg-row ${sender === 'bot' ? 'bot-row' : 'user-row'}`;

  if (sender === 'bot') {
    row.innerHTML = `
      <div class="bot-avatar small">🌱</div>
      <div class="bot-msg"></div>
    `;
    row.querySelector('.bot-msg').textContent = text;
  } else {
    row.innerHTML = `<div class="user-msg"></div>`;
    row.querySelector('.user-msg').textContent = text;
  }

  chatWindow.appendChild(row);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return row;
}

// ---------- Call YOUR backend chatbot instead of Gemini ----------
async function getAIResponse(question) {
  const response = await fetch(`${BACKEND_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: question })
  });

  if (!response.ok) {
    throw new Error("Backend request failed: " + response.status);
  }

  const data = await response.json();

  if (!data.success) {
    throw new Error(data.error || "Unknown error");
  }

  return data.response;
}

// ---------- Handle sending a message ----------
async function handleSend() {
  const question = chatInput.value.trim();
  if (question === '') return;

  addMessage(question, 'user');
  chatInput.value = '';

  const typingRow = addMessage('Typing...', 'bot');

  try {
    const answer = await getAIResponse(question);
    typingRow.querySelector('.bot-msg').textContent = answer;
  } catch (err) {
    typingRow.querySelector('.bot-msg').textContent =
      "Sorry, I couldn't connect to the server. Make sure the backend (app.py) is running.";
    console.error(err);
  }

  chatWindow.scrollTop = chatWindow.scrollHeight;
}

sendBtn.addEventListener('click', handleSend);
chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') handleSend();
});
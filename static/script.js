// ============================================
// CONFIG
// ============================================
const BACKEND_URL = '';

// ============================================
// HERO PARALLAX
// ============================================
function moveHeroBackground(e) {
    const hero = document.getElementById('hero-section');
    const x = (e.clientX / window.innerWidth) * 100;
    const y = (e.clientY / window.innerHeight) * 100;
    hero.style.backgroundPosition = `${x}% ${y}%`;
}

// ============================================
// UPLOAD MODAL
// ============================================
function openUploadModal() {
    document.getElementById('upload-modal').classList.remove('hidden');
}

function closeUploadModal() {
    document.getElementById('upload-modal').classList.add('hidden');
}

// Store the currently selected file globally so runAIScan can access it too
let currentFile = null;

// ============================================
// HANDLE IMAGE UPLOAD → SHOW PREVIEW → CALL BACKEND
// ============================================
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    currentFile = file;

    const reader = new FileReader();
    reader.onload = function (e) {
        document.getElementById('uploaded-img').src = e.target.result;
        closeUploadModal();
        // Automatically send to backend for real prediction
        detectPlantDisease(file);
    };
    reader.readAsDataURL(file);
}

// ============================================
// SEND IMAGE TO FLASK BACKEND & GET REAL PREDICTION
// ============================================
async function detectPlantDisease(imageFile) {
    showLoading(true);

    const formData = new FormData();
    formData.append('file', imageFile);

    try {
        const response = await fetch(`${BACKEND_URL}/predict`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Prediction failed');
        }

        renderPredictionResult(data);
        showResultsCard();

    } catch (error) {
        console.error("Backend connection failed:", error);
        alert("⚠️ Could not connect to the AI server. Make sure the backend (app.py) is running on port 5000.");
    } finally {
        showLoading(false);
    }
}

// ============================================
// UPDATE THE RESULT CARD WITH REAL BACKEND DATA
// ============================================
function renderPredictionResult(data) {
    const pred = data.prediction;
    const details = data.disease_details;

    // Title
    const title = pred.is_healthy
        ? `${pred.crop} — Healthy ✅`
        : `${pred.crop} — ${pred.disease.replace(/_/g, ' ')}`;
    document.getElementById('disease-title').textContent = title;

    // Confidence bar
    const confidencePercent = (pred.confidence * 100).toFixed(1);
    document.getElementById('confidence-bar-fill').style.width = `${confidencePercent}%`;
    document.getElementById('confidence-text').textContent = `Confidence: ${confidencePercent}%`;

    // Info blocks
    if (details) {
        document.getElementById('info-symptoms').textContent = details.symptoms || '—';
        document.getElementById('info-cause').textContent = details.cause || '—';
        document.getElementById('info-treatment').textContent = details.treatment || '—';
        document.getElementById('info-prevention').textContent = details.prevention || '—';
    }

    // Also push the chatbot's formatted message into the floating chat window
    if (data.chatbot_response) {
        addBotMessageToFloatingChat(data.chatbot_response);
    }
}

// ============================================
// LOADING OVERLAY HELPERS
// ============================================
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (!overlay) return;
    overlay.classList.toggle('hidden', !show);
}

// ============================================
// RESULTS CARD VISIBILITY
// ============================================
function showResultsCard() {
    const resultBox = document.getElementById('result-box');
    resultBox.classList.remove('hidden');
    resultBox.scrollIntoView({ behavior: 'smooth' });
}

function toggleDiseaseInfo() {
    const content = document.getElementById('disease-info-content');
    const btnText = document.getElementById('info-btn-text');
    const arrow = document.getElementById('info-arrow');

    content.classList.toggle('hidden');

    if (content.classList.contains('hidden')) {
        btnText.textContent = "View Disease Information";
        arrow.className = "fa-solid fa-chevron-down";
    } else {
        btnText.textContent = "Hide Disease Information";
        arrow.className = "fa-solid fa-chevron-up";
    }
}

function resetApp() {
    document.getElementById('result-box').classList.add('hidden');
    document.getElementById('disease-info-content').classList.add('hidden');
    currentFile = null;
    document.getElementById('hero-section').scrollIntoView({ behavior: 'smooth' });
}

// ============================================
// "AI SCANS IT" STEP CARD — reuse last uploaded file
// ============================================
function runAIScan() {
    if (!currentFile) {
        alert("Please upload a leaf image first using 'Upload Image'!");
        openUploadModal();
        return;
    }
    detectPlantDisease(currentFile);
}

// ============================================
// FLOATING CHATBOT (connected to backend /chat)
// ============================================
function toggleChatbot() {
    const modal = document.getElementById('chatbot-modal');
    modal.classList.toggle('hidden');
}

function addBotMessageToFloatingChat(text) {
    const chatBody = document.getElementById('chat-messages');
    const botMsg = document.createElement('div');
    botMsg.className = 'message bot-message';
    botMsg.style.whiteSpace = 'pre-wrap';
    botMsg.textContent = text;
    chatBody.appendChild(botMsg);
    chatBody.scrollTop = chatBody.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;

    const chatBody = document.getElementById('chat-messages');

    // Show user's message
    const userMsg = document.createElement('div');
    userMsg.className = 'message user-message';
    userMsg.textContent = text;
    chatBody.appendChild(userMsg);

    input.value = '';
    chatBody.scrollTop = chatBody.scrollHeight;

    // Show temporary "typing..." bubble
    const typingMsg = document.createElement('div');
    typingMsg.className = 'message bot-message';
    typingMsg.textContent = 'Typing...';
    chatBody.appendChild(typingMsg);
    chatBody.scrollTop = chatBody.scrollHeight;

    try {
        const response = await fetch(`${BACKEND_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();

        typingMsg.textContent = data.success
            ? data.response
            : "⚠️ Sorry, something went wrong.";
        typingMsg.style.whiteSpace = 'pre-wrap';

    } catch (error) {
        console.error("Chat backend error:", error);
        typingMsg.textContent = "⚠️ Could not connect to the chatbot server.";
    }

    chatBody.scrollTop = chatBody.scrollHeight;
}

function handleKeyPress(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
}

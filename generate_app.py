import os

os.makedirs('static', exist_ok=True)

main_py = """from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import ai_port

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

conversation_history = [
    {"role": "user", "content": ai_port.SYSTEM_PROMPT} 
]

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    global conversation_history
    user_msg = req.message
    
    conversation_history.append({"role": "user", "content": f"User Query: {user_msg}"})
    
    try:
        reply = ai_port.get_answer_from_llama(conversation_history)
        conversation_history.append({"role": "assistant", "content": reply})
        return {"response": reply}
    except Exception as e:
        conversation_history.pop() # Remove failed request
        return {"response": f"Server Error: {str(e)}"}

@app.get("/")
def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    print("Backend AI Server Starting...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
"""

index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SGBC AI Agent</title>
    <link rel="stylesheet" href="/static/style.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
</head>
<body>
    <div class="app-container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>SGBC AI Hub</h2>
                <button class="new-chat" onclick="location.reload()">+ New Chat</button>
            </div>
            <div class="sidebar-footer">
                v1.0 (Testing)
            </div>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <header>
                <div class="logo-text">Sudha Gopalakrishnan Brain Centre</div>
            </header>

            <div class="chat-container" id="chat-container">
                <div class="message assistant-message">
                    <div class="avatar assistant-avatar">SG</div>
                    <div class="message-content">
                        Hello! I am the SGBC AI Agent. How can I help you today?
                    </div>
                </div>
            </div>

            <div class="input-container">
                <div class="input-box">
                    <textarea id="user-input" placeholder="Message the AI Engine..." rows="1" oninput="this.style.height = '';this.style.height = this.scrollHeight + 'px'"></textarea>
                    <button id="send-btn">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M22 2L11 13" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
                <div class="footer-text">
                    Powered by IIT Madras & Llama-3.3-70B
                </div>
            </div>
        </div>
    </div>
    <script src="/static/script.js"></script>
</body>
</html>
"""

style_css = """* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Inter', sans-serif;
    background-color: #f8f9fa;
    color: #1d1d1f;
    height: 100vh;
    display: flex;
    overflow: hidden;
}
.app-container { display: flex; width: 100%; }
.sidebar {
    width: 260px;
    background-color: #f1f3f4;
    border-right: 1px solid #e0e0e0;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.sidebar-header h2 { font-size: 14px; color: #5f6368; margin-bottom: 20px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
.sidebar-footer { font-size: 12px; color: #9aa0a6; }
.new-chat {
    background-color: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 10px;
    width: 100%;
    text-align: left;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
}
.new-chat:hover { background-color: #eaeaea; }

.main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #ffffff;
}
header {
    height: 60px;
    border-bottom: 1px solid #eee;
    display: flex;
    align-items: center;
    padding: 0 24px;
}
.logo-text { font-size: 18px; color: #0096a6; font-weight: 600; letter-spacing: 0.5px; }

.chat-container {
    flex: 1;
    overflow-y: auto;
    padding: 40px 15%;
    display: flex;
    flex-direction: column;
    gap: 30px;
}
.message { display: flex; gap: 20px; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.avatar {
    width: 38px;
    height: 38px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 14px;
    flex-shrink: 0;
}
.assistant-avatar { background-color: #0096a6; color: white; }
.user-avatar { background-color: #f1f3f4; color: #1d1d1f; border: 1px solid #e0e0e0; }
.message-content {
    flex: 1;
    font-size: 16px;
    line-height: 1.6;
    color: #3c4043;
    padding-top: 6px;
}

.input-container { padding: 20px 15%; background: linear-gradient(0deg, #fff 80%, rgba(255,255,255,0) 100%); }
.input-box {
    display: flex;
    background-color: #f1f3f4;
    border-radius: 24px;
    padding: 12px 18px;
    border: 1px solid #e0e0e0;
    align-items: flex-end;
}
.input-box:focus-within {
    border-color: #0096a6;
    background-color: #fff;
    box-shadow: 0 4px 12px rgba(0,150,166,0.1);
}
textarea {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    resize: none;
    padding: 2px 10px;
    font-family: inherit;
    font-size: 16px;
    max-height: 200px;
    color: #1d1d1f;
}
#send-btn { background: none; border: none; cursor: pointer; color: #0096a6; padding: 4px 8px; border-radius: 50%; }
#send-btn:disabled { color: #ccc; cursor: not-allowed; }

.footer-text { text-align: center; font-size: 12px; color: #9aa0a6; margin-top: 12px; }

/* Typing animation */
.typing-dots { display: flex; align-items: center; gap: 4px; padding-top: 8px;}
.typing-dots span { width: 6px; height: 6px; background-color: #0096a6; border-radius: 50%; animation: bounce 1.4s infinite; }
.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
"""

script_js = """const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

function formatText(text) {
    let formatted = text.replace(/\\n/g, '<br>');
    formatted = formatted.replace(/\\*\\*(.*?)\\*\\*/g, '<strong></strong>');
    return formatted;
}

function addMessage(role, text) {
    const isUser = role === 'user';
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ' + (isUser ? 'user-message' : 'assistant-message');
    
    msgDiv.innerHTML = 
        <div class="avatar "></div>
        <div class="message-content"></div>
    ;
    
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTyping() {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message typing-msg';
    msgDiv.innerHTML = 
        <div class="avatar assistant-avatar">SG</div>
        <div class="message-content">
            <div class="typing-dots"><span></span><span></span><span></span></div>
        </div>
    ;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeTyping() {
    const el = document.querySelector('.typing-msg');
    if(el) el.remove();
}

async function handleSend() {
    const text = userInput.value.trim();
    if (!text) return;
    
    userInput.value = '';
    userInput.style.height = 'auto';
    addMessage('user', text);
    showTyping();
    sendBtn.disabled = true;
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: text})
        });
        const data = await response.json();
        removeTyping();
        addMessage('agent', data.response);
    } catch(err) {
        removeTyping();
        addMessage('agent', 'Error connecting to the AI Engine Server.');
    }
    
    sendBtn.disabled = false;
    userInput.focus();
}

sendBtn.addEventListener('click', handleSend);
userInput.addEventListener('keydown', (e) => {
    if(e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
});
"""

with open("main.py", "w", encoding="utf-8") as f: f.write(main_py)
with open("static/index.html", "w", encoding="utf-8") as f: f.write(index_html)
with open("static/style.css", "w", encoding="utf-8") as f: f.write(style_css)
with open("static/script.js", "w", encoding="utf-8") as f: f.write(script_js)

print("Generated Web App structure successfully.")

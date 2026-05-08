js_text = """const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const sidebarHistory = document.getElementById('sidebar-history');
const modeSelect = document.getElementById('chat-mode');

let currentMemory = JSON.parse(localStorage.getItem('sgbc_memory')) || [];
let hasGeneratedTitle = localStorage.getItem('sgbc_title') !== null;

function formatText(text) {
    let formatted = text.replace(/\\n/g, '<br>');
    formatted = formatted.replace(/\\*\\*(.*?)\\*\\*/g, '<strong></strong>');
    return formatted;
}

function renderMemory() {
    chatContainer.innerHTML = '';
    if (currentMemory.length === 0) {
        chatContainer.innerHTML = "<div class='message assistant-message'><div class='avatar assistant-avatar'>SG</div><div class='message-content'>Hello! I am the SGBC AI Agent. How can I help you today?</div></div>";
    } else {
        currentMemory.forEach(msg => {
            const isUser = msg.role === 'user';
            const msgDiv = document.createElement('div');
            msgDiv.className = 'message ' + (isUser ? 'user-message' : 'assistant-message');
            msgDiv.innerHTML = "<div class='avatar " + (isUser ? 'user-avatar' : 'assistant-avatar') + "'>" + (isUser ? 'You' : 'SG') + "</div>" +
                "<div class='message-content'>" + formatText(msg.content) + "</div>";
            chatContainer.appendChild(msgDiv);
        });
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    sidebarHistory.innerHTML = '';
    const storedTitle = localStorage.getItem('sgbc_title');
    if (storedTitle && storedTitle !== 'New Chat') {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerText = storedTitle;
        sidebarHistory.prepend(historyItem);
    }
}
renderMemory();

function addMessage(role, text) {
    const isUser = role === 'user';
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ' + (isUser ? 'user-message' : 'assistant-message');
    msgDiv.innerHTML = "<div class='avatar " + (isUser ? 'user-avatar' : 'assistant-avatar') + "'>" + (isUser ? 'You' : 'SG') + "</div>" +
        "<div class='message-content'>" + formatText(text) + "</div>";
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTyping() {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message typing-msg assistant-message';
    msgDiv.innerHTML = "<div class='avatar assistant-avatar'>SG</div>" +
        "<div class='message-content'><div class='typing-dots'><span></span><span></span><span></span></div></div>";
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeTyping() {
    const el = document.querySelector('.typing-msg');
    if(el) el.remove();
}

async function generateTitleAndSave() {
    try {
        const titleResponse = await fetch('/generate_title', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({history: currentMemory, mode: "short"})
        });
        const titleData = await titleResponse.json();
        
        if (titleData.title !== 'New Chat') {
            localStorage.setItem('sgbc_title', titleData.title);
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.innerText = titleData.title;
            sidebarHistory.prepend(historyItem);
        }
    } catch(err) {} 
}

async function handleSend() {
    const text = userInput.value.trim();
    if (!text) return;
    
    userInput.value = '';
    userInput.style.height = 'auto';
    addMessage('user', text);
    showTyping();
    sendBtn.disabled = true;
    
    currentMemory.push({role: 'user', content: text});
    localStorage.setItem('sgbc_memory', JSON.stringify(currentMemory));
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({history: currentMemory, mode: modeSelect.value})
        });
        const data = await response.json();
        removeTyping();
        
        if (data.error) {
            addMessage('agent', 'Backend Error: ' + data.error);
            currentMemory.pop(); 
            localStorage.setItem('sgbc_memory', JSON.stringify(currentMemory));
        } else {
            addMessage('agent', data.response);
            currentMemory.push({role: 'assistant', content: data.response});
            localStorage.setItem('sgbc_memory', JSON.stringify(currentMemory));
            
            if(!hasGeneratedTitle) {
                hasGeneratedTitle = true;
                generateTitleAndSave();
            }
        }
    } catch(err) {
        removeTyping();
        addMessage('agent', 'Error connecting to the API.');
        currentMemory.pop(); 
        localStorage.setItem('sgbc_memory', JSON.stringify(currentMemory));
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

document.querySelector('.new-chat').addEventListener('click', () => {
    currentMemory = [];
    hasGeneratedTitle = false;
    localStorage.removeItem('sgbc_memory');
    localStorage.removeItem('sgbc_title');
    sidebarHistory.innerHTML = '';
    chatContainer.innerHTML = "<div class='message assistant-message'>" +
        "<div class='avatar assistant-avatar'>SG</div>" +
        "<div class='message-content'>Hello! I am the SGBC AI Agent. How can I help you today?</div></div>";
});
"""

with open('static/script.js', 'w', encoding='utf-8') as f:
    f.write(js_text)
print("Updated static/script.js to use localStorage.")

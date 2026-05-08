js_text = """const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const sidebarHistory = document.getElementById('sidebar-history');
const modeSelect = document.getElementById('chat-mode');

let chats = JSON.parse(localStorage.getItem('sgbc_chats')) || {};
let activeChatId = localStorage.getItem('sgbc_active_chat') || null;

function generateId() {
    return Math.random().toString(36).substring(2, 15);
}

if (!activeChatId || !chats[activeChatId]) {
    createNewChat();
}

function createNewChat() {
    activeChatId = generateId();
    chats[activeChatId] = {
        title: "New Chat",
        memory: []
    };
    saveState();
    renderUI();
}

function saveState() {
    localStorage.setItem('sgbc_chats', JSON.stringify(chats));
    localStorage.setItem('sgbc_active_chat', activeChatId);
}

function formatText(text) {
    let formatted = text.replace(/\\n/g, '<br>');
    formatted = formatted.replace(/\\*\\*(.*?)\\*\\*/g, '<strong></strong>');
    return formatted;
}

function renderUI() {
    chatContainer.innerHTML = '';
    const currentMemory = chats[activeChatId].memory;
    
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
    }
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    sidebarHistory.innerHTML = '';
    
    const chatKeys = Object.keys(chats).reverse();
    
    chatKeys.forEach(id => {
        const item = document.createElement('div');
        item.className = 'history-item';
        if (id === activeChatId) {
            item.style.backgroundColor = '#d3e3fd'; 
            item.style.fontWeight = 'bold';
        }
        item.innerText = chats[id].title;
        
        item.addEventListener('click', () => {
            activeChatId = id;
            saveState();
            renderUI();
        });
        
        sidebarHistory.appendChild(item);
    });
}
renderUI();

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
            body: JSON.stringify({history: chats[activeChatId].memory, mode: "short"})
        });
        const titleData = await titleResponse.json();
        
        if (titleData.title !== 'New Chat') {
            chats[activeChatId].title = titleData.title;
            saveState();
            renderUI();
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
    
    const isFirstMessage = chats[activeChatId].memory.length === 0;
    
    chats[activeChatId].memory.push({role: 'user', content: text});
    saveState();
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({history: chats[activeChatId].memory, mode: modeSelect.value})
        });
        const data = await response.json();
        removeTyping();
        
        if (data.error) {
            addMessage('agent', 'Backend Error: ' + data.error);
            chats[activeChatId].memory.pop(); 
            saveState();
        } else {
            addMessage('agent', data.response);
            chats[activeChatId].memory.push({role: 'assistant', content: data.response});
            saveState();
            
            if (isFirstMessage) {
                generateTitleAndSave(); 
            }
        }
    } catch(err) {
        removeTyping();
        addMessage('agent', 'Error connecting to the API.');
        chats[activeChatId].memory.pop(); 
        saveState();
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
    createNewChat();
});
"""

with open('static/script.js', 'w', encoding='utf-8') as f:
    f.write(js_text)
print("Updated static/script.js to use full multi-session chatting.")

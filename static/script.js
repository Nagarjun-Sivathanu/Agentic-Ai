const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const sidebarHistory = document.getElementById('sidebar-history');
const modeSelect = document.getElementById('chat-mode');
const insightPanel = document.getElementById('insight-panel');
const insightOverlay = document.getElementById('insight-overlay');
const insightClose = document.getElementById('insight-close');
const insightHeader = document.getElementById('insight-header');
const insightBody = document.getElementById('insight-body');

let currentMemory = [];
let hasGeneratedTitle = false;

// --- RICH MARKDOWN RENDERER ---
function formatMarkdown(text) {
    if (!text) return "";
    
    // A. Protocols (Global search & extract)
    let visualsHTML = "";
    
    // 1. Map Embeds
    const mapRegex = /MAP_EMBED:(https?:\/\/[^\s\n\r]+)/gi;
    text = text.replace(mapRegex, (match, url) => {
        visualsHTML += `<div class="map-container"><iframe src="${url}"></iframe></div>`;
        return "";
    });
    
    // 2. Image Displays
    const imgRegex = /IMAGE_DISPLAY:(https?:\/\/[^\s\n\r]+)/gi;
    text = text.replace(imgRegex, (match, url) => {
        visualsHTML += `
            <div class="visual-container">
                <div class="image-card" onclick="window.open('${url}', '_blank')">
                    <img src="${url}" loading="lazy" alt="Visual Insight">
                    <div class="image-overlay">Click to view high-res</div>
                </div>
            </div>`;
        return "";
    });

    // 3. Filter internal protocol triggers
    text = text.replace(/TOOL_REQUEST:[^\n]*/gi, "");

    // B. Markdown Core (Simple)
    let html = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

    // Tables
    const tableRegex = /\|(.+)\|.*\n\|([-| :]+)\|.*\n((\|.*\|.*\n)*)/g;
    html = html.replace(tableRegex, (match, header, divider, rows) => {
        const headers = header.split('|').filter(h => h.trim()).map(h => `<th>${h.trim()}</th>`).join('');
        const rowHTML = rows.trim().split('\n').map(row => {
            const cells = row.split('|').filter(c => c.trim()).map(c => `<td>${c.trim()}</td>`).join('');
            return `<tr>${cells}</tr>`;
        }).join('');
        return `<div style="overflow-x:auto;"><table><thead><tr>${headers}</tr></thead><tbody>${rowHTML}<tbody></table></div>`;
    });

    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\[\[(.*?)\]\]/g, (match, term) => {
        return `<span class="insight-link" onclick="openInsight('${term.replace(/'/g, "\\'").replace(/"/g, '\\"')}')">${term}</span>`;
    });
    html = html.replace(/^\* (.*$)/gim, '<li>$1</li>');
    html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
    html = html.replace(/\n/g, '<br>');

    return visualsHTML + html;
}


// --- MESSAGE RENDERING ---
function addMessage(role, text) {
    const isUser = role === 'user';
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ' + (isUser ? 'user-message' : 'assistant-message');
    
    const avatar = isUser ? '<div class="avatar user-avatar">You</div>' : '<div class="avatar assistant-avatar">SG</div>';
    const content = `<div class="message-content">${isUser ? text : formatMarkdown(text)}</div>`;
    
    msgDiv.innerHTML = avatar + content;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTyping() {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message typing-msg assistant-message';
    msgDiv.innerHTML = `<div class="avatar assistant-avatar">SG</div>
        <div class="message-content"><div class="typing-dots"><span></span><span></span><span></span></div></div>`;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeTyping() {
    const el = document.querySelector('.typing-msg');
    if(el) el.remove();
}

// --- INSIGHT PANEL LOGIC ---
async function openInsight(term) {
    insightHeader.innerText = term;
    insightBody.innerHTML = '<div class="insight-loading"><div class="typing-dots"><span></span><span></span><span></span></div><p style="margin-top:20px; font-size:13px; color:#5f6368;">Analyzing context...</p></div>';
    
    insightPanel.classList.add('open');
    insightOverlay.classList.add('open');
    
    try {
        const response = await fetch('/insight', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                term: term,
                history: currentMemory.slice(-4) // Send last 4 messages for context
            })
        });
        const data = await response.json();
        
        let cleanText = data.breakdown.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        insightBody.innerHTML = `<div class="insight-content-inner">${cleanText}</div>`;
    } catch(err) {
        insightBody.innerHTML = '<p style="color:red;">Error fetching contextual insight.</p>';
    }
}

function closeInsight() {
    insightPanel.classList.remove('open');
    insightOverlay.classList.remove('open');
}

insightClose.onclick = closeInsight;
insightOverlay.onclick = closeInsight;

// --- APP LOGIC ---
async function generateTitleAndSave() {
    try {
        const titleResponse = await fetch('/generate_title', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({history: currentMemory, mode: "short"})
        });
        const titleData = await titleResponse.json();
        
        if (titleData.title) {
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
        } else {
            addMessage('agent', data.response);
            currentMemory.push({role: 'assistant', content: data.response});
            if(!hasGeneratedTitle) {
                hasGeneratedTitle = true;
                generateTitleAndSave();
            }
        }
    } catch(err) {
        removeTyping();
        addMessage('agent', 'Error connecting to the SGBC Engine.');
        currentMemory.pop(); 
    }
    
    sendBtn.disabled = false;
    userInput.focus();
}

// Listeners
sendBtn.onclick = handleSend;
userInput.onkeydown = (e) => {
    if(e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
};

document.getElementById('new-chat-btn').onclick = () => {
    currentMemory = [];
    hasGeneratedTitle = false;
    chatContainer.innerHTML = `<div class="message assistant-message">
        <div class="avatar assistant-avatar">SG</div>
        <div class="message-content">New session started. How can I help you today?</div>
    </div>`;
};

import os
os.makedirs('static', exist_ok=True)

main_py = """
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import ai_port

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    history: list
    mode: str = "short"

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        full_messages = [{"role": "system", "content": ai_port.SYSTEM_PROMPT}] + req.history
        reply = ai_port.get_answer_from_llama(full_messages, req.mode)
        return {"response": reply}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.post("/generate_title")
async def gen_title(req: ChatRequest):
    try:
        full_messages = [{"role": "system", "content": ai_port.SYSTEM_PROMPT}] + req.history
        title = ai_port.generate_chat_title(full_messages)
        return {"title": title}
    except Exception as e:
        return {"title": "New Chat"}

@app.get("/")
def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    print("Backend AI Server with Multi-Chat Starting...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
"""

ai_port_py = r'''
import openai
import wikipedia
from duckduckgo_search import DDGS

def execute_tool(tool_name, arguments):
    print(f"\n[SYSTEM] Executing actual tool: {tool_name} with arg: {arguments}")
    if tool_name == "wiki":
        try:
            search_results = wikipedia.search(arguments)
            if not search_results:
                return "Error: No wikipedia page found for this topic."
            best_match = search_results[0]
            result = wikipedia.summary(best_match, sentences=15)
            return result
        except wikipedia.exceptions.DisambiguationError as e:
            result = wikipedia.summary(e.options[0], sentences=15)
            return result
        except Exception as e:
            return f"Error searching wikipedia: {e}"
    elif tool_name == "calculate":
        try:
            return str(eval(arguments))
        except Exception as e:
            return f"Error evaluating math: {e}"
    elif tool_name == "search_web":
        try:
            results = DDGS().text(arguments, max_results=5)
            formatted = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
            return formatted if formatted else "No results found."
        except Exception as e:
            return f"Error searching web: {e}"
    return "Error: Unknown tool."

SYSTEM_PROMPT = """You are a highly detailed AI assistant. You have access to the following tools:

- Tool Name: search_web
  Description: Search DuckDuckGo. Use this AUTOMATICALLY if the user asks you to "search", or if you need current news/events.
  Arguments: query

- Tool Name: wiki
  Description: Search Wikipedia for facts about historical figures, places, or concepts.
  Arguments: 	opic

- Tool Name: calculate
  Description: Safely evaluate math equations.
  Arguments: expression
  
CRITICAL RULE: If you decide to use a tool, you MUST reply with ONLY this exact format and absolutely NO OTHER WORDS:
TOOL_REQUEST:<tool_name>|<argument_value>
"""

def generate_chat_title(messages_array):
    client = openai.OpenAI(base_url="http://dgx5.humanbrain.in:8999/v1", api_key="empty")
    title_messages = [ 
        {"role": "system", "content": "Generate a short, 3 to 4 word title describing the user's topic. Reply with ONLY the title string, no quotes."}
    ]
    title_messages.append(messages_array[1]) 
    completion = client.chat.completions.create(model='Llama-3.3-70B-Instruct', messages=title_messages, temperature=0.7, max_tokens=20)
    return completion.choices[0].message.content.strip()

def get_answer_from_llama(messages_array, mode="short"):
    client = openai.OpenAI(base_url="http://dgx5.humanbrain.in:8999/v1", api_key="empty")
    
    mode_instructions = ""
    if mode == "short":
        mode_instructions = "Keep your final answer extremely short, crisp, and to the point. No fluff."
    elif mode == "detailed":
        mode_instructions = "Present a large amount of detailed research data covering various aspects/regions."
    elif mode == "timeline":
        mode_instructions = "Focus primarily on historic changes and format the information strictly as a chronological timeline."
    elif mode == "integrated":
        mode_instructions = "Provide a comprehensive response that integrates a short crisp summary, extremely detailed research, and a clear historical timeline."
    
    messages_copy = list(messages_array)
    if len(messages_copy) > 0 and messages_copy[-1]["role"] == "user":
        original_content = messages_copy[-1]["content"]
        messages_copy[-1] = {
            "role": "user", 
            "content": f"{original_content}\n\n[USER PREFERENCE]: If you answer directly, {mode_instructions}"
        }

    completion = client.chat.completions.create(
        model = 'Llama-3.3-70B-Instruct',
        messages=messages_copy,
        temperature=0.3,
        frequency_penalty=1.0,
        top_p=0.5,
        max_tokens=2048,
        stream=False
    )
    
    response_text = completion.choices[0].message.content.strip()
    
    if "TOOL_REQUEST:" in response_text:
        print("\n[AI AGENT ALERT] -> The model wants to use a tool!")
        tool_call_line = ""
        for line in response_text.split('\n'):
            if "TOOL_REQUEST:" in line:
                tool_call_line = line
                break
                
        parts = tool_call_line.replace("TOOL_REQUEST:", "").split("|")
        tool_name = parts[0].strip()
        arguments = parts[1].strip() if len(parts) > 1 else ""
        
        tool_result = execute_tool(tool_name, arguments)
        messages_array.append({"role": "assistant", "content": response_text})
        
        if tool_name == "calculate":
            follow_up_prompt = f"Tool returned: {tool_result}\nProvide a very short, direct answer stating purely the math result. Do not elaborate."
        else:
            follow_up_prompt = f"Tool returned: {tool_result}\nProvide a detailed answer. IMPORTANT: {mode_instructions} DO NOT mention that you used a tool."
            
        messages_array.append({"role": "user", "content": follow_up_prompt})
        
        final_completion = client.chat.completions.create(
            model = 'Llama-3.3-70B-Instruct',
            messages=messages_array,
            temperature=0.4,
            max_tokens=2048
        )
        return final_completion.choices[0].message.content.strip()

    else:
        return response_text

if __name__ == '__main__':
    print("Run main.py")
'''

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
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>SGBC AI Hub</h2>
                <button class="new-chat">+ New Chat</button>
            </div>
            <div id="sidebar-history" style="flex:1; overflow-y:auto; margin-top:20px; display:flex; flex-direction:column; gap:5px;"></div>
            <div class="sidebar-footer">v1.0 (Testing)</div>
        </div>

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
                <div class="mode-selector" style="margin-bottom: 12px; display:flex; align-items:center; gap:10px;">
                    <span style="font-size:13px; font-weight:600; color:#5f6368;">Response Style:</span>
                    <select id="chat-mode" style="padding: 6px 10px; border-radius: 8px; border: 1px solid #e0e0e0; background: #f1f3f4; font-size: 13px; color: #1d1d1f; outline: none; cursor: pointer; font-family: inherit;">
                        <option value="short">Short & Concise</option>
                        <option value="detailed">Detailed Research</option>
                        <option value="timeline">Timeline & History</option>
                        <option value="integrated">Fully Integrated (All)</option>
                    </select>
                </div>
                <div class="input-box">
                    <textarea id="user-input" placeholder="Message the AI Engine..." rows="1" oninput="this.style.height = '';this.style.height = this.scrollHeight + 'px'"></textarea>
                    <button id="send-btn">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M22 2L11 13" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
                <div class="footer-text">Powered by IIT Madras & Llama-3.3-70B</div>
            </div>
        </div>
    </div>
    <script src="/static/script.js"></script>
</body>
</html>
"""

script_js = """
const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const sidebarHistory = document.getElementById('sidebar-history');
const modeSelect = document.getElementById('chat-mode');

let currentMemory = [];
let hasGeneratedTitle = false;

function formatText(text) {
    let formatted = text.replace(/\\n/g, '<br>');
    formatted = formatted.replace(/\\*\\*(.*?)\\*\\*/g, '<strong></strong>');
    return formatted;
}

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
        addMessage('agent', 'Error connecting to the API.');
        currentMemory.pop(); 
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
    chatContainer.innerHTML = "<div class='message assistant-message'>" +
        "<div class='avatar assistant-avatar'>SG</div>" +
        "<div class='message-content'>Hello! I am the SGBC AI Agent. How can I help you today?</div></div>";
});
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

.history-item { padding:8px 12px; background:#fff; border-radius:6px; font-size:13px; color:#3c4043; cursor:pointer; }
.history-item:hover { background:#eaeaea; }
"""

with open('main.py', 'w', encoding='utf-8') as f: f.write(main_py)
with open('ai_port.py', 'w', encoding='utf-8') as f: f.write(ai_port_py)
with open('static/index.html', 'w', encoding='utf-8') as f: f.write(index_html)
with open('static/style.css', 'w', encoding='utf-8') as f: f.write(style_css)
with open('static/script.js', 'w', encoding='utf-8') as f: f.write(script_js)
print("SUCCESS: REBUILT APP with dropdown styling")

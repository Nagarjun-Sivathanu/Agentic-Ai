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

class InsightRequest(BaseModel):
    term: str
    history: list = []

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        # Fixed: SYSTEM_PROMPT is now a dynamic function get_system_prompt()
        full_messages = [{"role": "system", "content": ai_port.get_system_prompt()}] + req.history
        reply = ai_port.get_answer_from_llama(full_messages, req.mode)
        return {"response": reply}
    except Exception as e:
        return {"error": str(e)}

@app.post("/generate_title")
async def gen_title(req: ChatRequest):
    try:
        full_messages = [{"role": "system", "content": ai_port.get_system_prompt()}] + req.history
        title = ai_port.generate_chat_title(full_messages)
        return {"title": title}
    except Exception as e:
        return {"title": "New Chat"}

@app.post("/insight")
async def get_insight(req: InsightRequest):
    try:
        breakdown = ai_port.get_insight_breakdown(req.term, req.history)
        return {"breakdown": breakdown}
    except Exception as e:
        return {"breakdown": f"Could not fetch insight for {req.term}."}

@app.get("/")
def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    print("Backend AI Server v2.1.2 (Stable) Starting...")
    uvicorn.run(app, host="127.0.0.1", port=8000)

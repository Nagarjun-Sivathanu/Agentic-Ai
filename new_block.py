import openai
import wikipedia
from duckduckgo_search import DDGS
import yfinance as yf
import requests
import datetime
import re
import urllib.parse

def extract_ticker(text):
    common_words = {"WHAT", "IS", "THE", "PRICE", "OF", "STOCK", "GET", "ME", "FOR", "AND", "ANY", "NEWS", "ABOUT"}
    text_clean = re.sub(r'[^A-Z\s]', '', text.upper())
    words = text_clean.split()
    for w in words:
        if 1 <= len(w) <= 5 and w not in common_words: return w
    return words[0] if words else ""

def get_verified_image(query):
    """Sourcing verified photographs from Wikipedia Media API ONLY."""
    try:
        headers = {"User-Agent": "SGBC-Research-Agent/1.0 (verified@sgbc.iitm.ac.in)"}
        URL = "https://en.wikipedia.org/w/api.php"
        # Search
        search_params = {"action": "query", "list": "search", "srsearch": query, "format": "json"}
        search_res = requests.get(URL, params=search_params, headers=headers).json()
        if not search_res.get("query", {}).get("search"): return None
        title = search_res["query"]["search"][0]["title"]
        
        # Pithumb
        img_params = {"action": "query", "format": "json", "prop": "pageimages", "titles": title, "pithumbsize": 1024}
        img_res = requests.get(url=URL, params=img_params, headers=headers).json()
        pages = img_res.get("query", {}).get("pages", {})
        for p in pages:
            if "thumbnail" in pages[p]:
                return pages[p]["thumbnail"]["source"]
    except Exception: return None
    return None

def execute_tool(tool_name, arguments):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n[TOOL] {tool_name} ({now}) => {arguments}")
    if tool_name == "wiki":
        try:
            results = wikipedia.search(arguments)
            if not results: return f"WIKI ERROR: No entry."
            return f"(As of {now} | From Wiki) {wikipedia.summary(results[0], sentences=5)}"
        except Exception as e: return f"WIKI ERROR: {e}"
    elif tool_name == "source_image":
        img_url = get_verified_image(arguments)
        if img_url:
            return f"VERIFIED_PHOTO: {arguments}\nIMAGE_DISPLAY:{img_url}"
        return f"IMAGE ERROR: No verified photograph found for '{arguments}'. AI generation is disabled."
    elif tool_name == "search_web":
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.news(arguments, max_results=3)]
                if not results: results = [r for r in ddgs.text(arguments, max_results=3)]
                return "\n".join([f"(As of {now} | From Web) {r.get('title')}: {r.get('body', r.get('snippet',''))}" for r in results]) or "WEB ERROR: No data."
        except Exception as e: return f"WEB ERROR: {e}"
    elif tool_name == "stock_data":
        ticker = extract_ticker(arguments)
        try:
            t = yf.Ticker(ticker); info = t.info
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            if not price: return f"STOCK ERROR: No price for {ticker}."
            return f"(As of {now} | From Stock) {ticker}: {price} {info.get('currency')} | Co: {info.get('longName')}"
        except Exception as e: return f"STOCK ERROR: {e}"
    elif tool_name == "location":
        try:
            headers = {"User-Agent": "SGBC-Research-Agent/1.0"}
            resp = requests.get("https://nominatim.openstreetmap.org/search", params={"q": arguments, "format": "json", "limit": 1}, headers=headers, timeout=10)
            data = resp.json()
            if not data: return f"LOCATION ERROR: No results for '{arguments}'"
            r = data[0]; lat, lon = r["lat"], r["lon"]
            return f"Location: {r.get('display_name', arguments)}\nLat/Lon: {lat}, {lon}\nMAP_EMBED:https://www.openstreetmap.org/export/embed.html?bbox={float(lon)-0.01},{float(lat)-0.005},{float(lon)+0.01},{float(lat)+0.005}&layer=mapnik&marker={lat},{lon}"
        except Exception as e: return f"LOCATION ERROR: {e}"
    return f"ERROR: Unknown tool {tool_name}"

def detect_required_tools(query):
    q = query.lower()
    extras = []
    if any(k in q for k in ["show me","photo","picture","visual","see"]):
        extras.append(("source_image", query))
    if any(k in q for k in ["stock","price","nvidia","nasdaq","msft"]):
        extras.append(("stock_data", query)); extras.append(("search_web", query + " update"))
    return extras

def get_system_prompt():
    now = datetime.datetime.now().strftime("%A, %B %d, %Y")
    return f"""You are a Fact-First AI Researcher at SGBC. Today: {now}.
PURE FACT VISUAL POLICY:
- You ONLY have access to real-world verified photographs via the `source_image` tool.
- AI Image Generation (Pollinations/DALL-E) is PERMANENTLY DISABLED.
- If a verified photo is not found, explain that no real-world visual is available.
- Cite using [Stock], [Web], [Wiki]. No [AI] tags.
"""

def get_answer_from_llama(messages_array, mode="short"):
    client = openai.OpenAI(base_url="http://dgx5.humanbrain.in:8999/v1", api_key="empty")
    msgs = [{"role": "system", "content": get_system_prompt()}] + messages_array
    r = client.chat.completions.create(model="Llama-3.3-70B-Instruct", messages=msgs, temperature=0.3)
    resp = r.choices[0].message.content.strip()
    tools = []
    if "TOOL_REQUEST:" in resp:
        for line in resp.split("\n"):
            if "TOOL_REQUEST:" in line:
                p = line.replace("TOOL_REQUEST:","").split("|")
                if len(p) >= 2: tools.append((p[0].strip(), p[1].strip()))
    
    pre = detect_required_tools(messages_array[-1]["content"])
    all_t = list(tools); s = {n for n,_ in tools}
    for n,a in pre:
        if n not in s: all_t.append((n,a)); s.add(n)
        
    if all_t:
        data_res, imagery = [], []
        for n,a in all_t:
            res = execute_tool(n, a)
            for line in res.split("\n"):
                if line.startswith("MAP_EMBED:"): imagery.append(line)
                elif line.startswith("IMAGE_DISPLAY:"): imagery.append(line)
            res_clean = "\n".join([l for l in res.split("\n") if not l.startswith("MAP_EMBED:") and not l.startswith("IMAGE_DISPLAY:")])
            data_res.append(f"VERIFIED DATA ({n}):\n{res_clean}")

        messages_array.append({"role":"assistant","content":resp})
        p = f"REAL-WORLD EVIDENCE:\n{'\n\n'.join(data_res)}\n\nFINAL REPORT:\n- Cite [Source].\n- Must include protocol lines (if any): " + "\n".join(imagery) + "\n- If tool reported 'No verified photograph found', inform the user specifically."
        messages_array.append({"role":"user","content":p})
        final = client.chat.completions.create(model="Llama-3.3-70B-Instruct", messages=messages_array, temperature=0.4, max_tokens=2048)
        return final.choices[0].message.content.strip()
    return resp

def generate_chat_title(messages_array):
    client = openai.OpenAI(base_url="http://dgx5.humanbrain.in:8999/v1", api_key="empty")
    r = client.chat.completions.create(model="Llama-3.3-70B-Instruct", messages=[{"role":"system","content":"3 words:"}, messages_array[1]], temperature=0.7)
    return r.choices[0].message.content.strip()

def get_insight_breakdown(term, history=[]):
    client = openai.OpenAI(base_url="http://dgx5.humanbrain.in:8999/v1", api_key="empty")
    ctx = " | ".join([m["content"] for m in history[-2:] if m["role"] == "user"])
    m = [{"role":"system","content":f"Explain [[{term}]] in context of: {ctx}."}, {"role":"user","content":f"Explain: {term}"}]
    r = client.chat.completions.create(model="Llama-3.3-70B-Instruct", messages=m, temperature=0.4, max_tokens=350)
    return r.choices[0].message.content.strip()

if __name__ == "__main__": print("Run main.py")

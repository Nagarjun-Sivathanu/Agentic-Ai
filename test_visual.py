import ai_port

print("=== DIAGNOSTIC: VISUAL PROTOCOL CHECK ===")
messages = [{"role": "user", "content": "Show me an image of a red sports car."}]
res = ai_port.get_answer_from_llama(messages, mode="short")
print(f"RAW OUTPUT:\n{res}\n")

if "IMAGE_DISPLAY:" in res:
    print("PROTOCOL DETECTED")
    parts = res.split("IMAGE_DISPLAY:")
    if len(parts) > 1:
        url = parts[1].split("\n")[0].strip()
        print(f"EXTRACTED URL: {url}")
else:
    print("PROTOCOL MISSING - HALLUCINATION LIKELY")

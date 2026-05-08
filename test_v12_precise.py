import ai_port

print("=== TEST 1: PRECISE CITATION CHECK ===")
messages = [{"role": "user", "content": "Tell me about NVIDIA founders and their current stock price."}]
res = ai_port.get_answer_from_llama(messages, mode="short")
print(f"Response:\n{res}\n")

lines = res.split("\n")
founder_line_tagged = False
for line in lines:
    if "founded" in line.lower() or "huang" in line.lower():
        if "[Stock]" in line or "[Web]" in line or "[Wiki]" in line:
            founder_line_tagged = True
            print(f"BAD LINE: {line}")

if not founder_line_tagged:
    print("PASS: Founder information is NOT mis-tagged.")
else:
    print("FAIL: Founder information IS mis-tagged.")

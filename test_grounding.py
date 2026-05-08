import ai_port

# Test 1: Forced "I don't know" for non-existent stock
print("=== TEST 1: NO HALLUCINATION TEST ===")
messages = [{"role": "user", "content": "What is the current stock price of MADE_UP_X_CORP and their latest news?"}]
res = ai_port.get_answer_from_llama(messages, mode="short")
print(f"Response: {res}")
has_hallucination = any(char.isdigit() for char in res) and "$" in res # If it gives a price
print(f"Factual Guard Check: {'FAIL' if has_hallucination else 'PASS'}")

# Test 2: Citation Check
print("\n=== TEST 2: CITATION CHECK ===")
messages2 = [{"role": "user", "content": "Tell me about Microsoft stock price."}]
res2 = ai_port.get_answer_from_llama(messages2, mode="short")
print(f"Response: {res2}")
has_citation = "[Stock]" in res2 or "(Source: Stock)" in res2 or "[Web]" in res2
print(f"Citation Check: {'PASS' if has_citation else 'FAIL'}")

if not has_hallucination and has_citation:
    print("\n=== GROUNDING VERIFIED ===")
else:
    print("\n=== GROUNDING FAILED ===")

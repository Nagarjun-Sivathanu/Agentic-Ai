import ai_port

# Test 1: Full Synthesis for NVIDIA
print("=== TEST 1: RICH FORMATTING SYNTHESIS ===")
messages = [
    {"role": "user", "content": "Tell me about NVIDIA stock stats and latest news."}
]
response = ai_port.get_answer_from_llama(messages, mode="detailed")
print("\nResponse Output:\n")
print(response)

# Check for keywords
has_headings = "##" in response
has_bold = "**" in response
has_brackets = "[[" in response

print(f"\nVerification:")
print(f"- Has ## Headings: {has_headings}")
print(f"- Has **Bold**: {has_bold}")
print(f"- Has [[Brackets]]: {has_brackets}")

assert has_headings, "FAIL: No headings found"
assert has_bold, "FAIL: No bold text found"
assert has_brackets, "FAIL: No technical term brackets found"

print("\n=== RENDERING TEST PASSED ===")

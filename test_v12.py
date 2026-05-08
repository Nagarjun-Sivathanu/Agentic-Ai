import ai_port

# Test: Only Stock data provided, but ask about CEO (which tool won't return).
print("=== TEST 1: CITATION INTEGRITY CHECK ===")
messages = [{"role": "user", "content": "What is NVIDIA's current stock price and who founded the company?"}]
res = ai_port.get_answer_from_llama(messages, mode="short")
print(f"Response Body:\n{res}\n")

# Logic:
# 1. Price should be cited as [Stock].
# 2. Founder name (if used from internal memory) should NOT be cited as [Stock].

has_stock_tag = "[Stock]" in res
is_founder_cited_wrong = "founded" in res.lower() and "[Stock]" in res[res.lower().find("founded"):]

print(f"Price tagged [Stock]: {has_stock_tag}")
print(f"Founder falsely tagged [Stock]: {is_founder_cited_wrong}")

if has_stock_tag and not is_founder_cited_wrong:
    print("\n=== CITATION INTEGRITY PASS ===")
else:
    print("\n=== CITATION INTEGRITY FAIL ===")

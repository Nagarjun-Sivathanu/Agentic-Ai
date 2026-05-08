import ai_port

# Test 1: Financial Context
print("=== TEST 1: FINANCIAL CONTEXT ===")
history1 = [{"role": "user", "content": "I am looking for high-performance stocks in the chip industry."}]
res1 = ai_port.get_insight_breakdown("NVIDIA", history1)
print(f"Explanation (Financial): {res1[:300]}...")

# Test 2: Technological/Historical Context
print("\n=== TEST 2: TECH CONTEXT ===")
history2 = [{"role": "user", "content": "I want to learn about the history of graphics rendering and video games."}]
res2 = ai_port.get_insight_breakdown("NVIDIA", history2)
print(f"Explanation (Gaming): {res2[:300]}...")

# Verify they are different
if res1.lower() != res2.lower():
    print("\nPASS: Insights are context-aware (Different explanations for different histories)")
else:
    print("\nFAIL: Insights are identical")

import ai_port

print("=== TEST 1: FACTUAL SOURCING ===")
res1 = ai_port.get_answer_from_llama([{"role":"user","content":"Show me NVIDIA headquarters."}], mode="short")
print(f"NVIDIA Response:\n{res1}\n")
has_wiki = "wikimedia.org" in res1
print(f"Wiki Sourcing: {'PASS' if has_wiki else 'FAIL'}")

print("\n=== TEST 2: CREATIVE GENERATION ===")
res2 = ai_port.get_answer_from_llama([{"role":"user","content":"Show me a futuristic city on Mars."}], mode="short")
print(f"Mars Response:\n{res2}\n")
has_pollinations = "pollinations.ai" in res2
print(f"AI Generation: {'PASS' if has_pollinations else 'FAIL'}")

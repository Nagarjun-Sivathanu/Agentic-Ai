import ai_port

print("=== TEST 1: REAL OBJECT (EXPECT PHOTO) ===")
res1 = ai_port.get_answer_from_llama([{"role":"user","content":"Show me the Eiffel Tower."}], mode="short")
print(f"Eiffel Response:\n{res1}\n")
has_photo = "IMAGE_DISPLAY:https://upload.wikimedia.org" in res1
print(f"Verified Photography: {'PASS' if has_photo else 'FAIL'}")

print("\n=== TEST 2: ABSTRACT CONCEPT (EXPECT REJECTION) ===")
res2 = ai_port.get_answer_from_llama([{"role":"user","content":"Show me a futuristic cat on Mars."}], mode="short")
print(f"Mars Cat Response:\n{res2}\n")
has_rejection = "verified photograph" in res2.lower() and "pollinations.ai" not in res2.lower()
print(f"Generative Rejection: {'PASS' if has_rejection else 'FAIL'}")

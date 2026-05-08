import ai_port

print("=== TEST 1: IMAGE GENERATION PROTOCOL ===")
messages = [{"role": "user", "content": "Show me a futuristic city image."}]
res = ai_port.get_answer_from_llama(messages, mode="short")
print(f"Response:\n{res}\n")

has_image_protocol = "IMAGE_DISPLAY:https://image.pollinations.ai/prompt/" in res
if has_image_protocol:
    print("PASS: Image generation protocol detected.")
else:
    print("FAIL: Image protocol missing.")

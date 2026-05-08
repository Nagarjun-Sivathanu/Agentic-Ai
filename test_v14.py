import ai_port

print("=== TEST 1: VISUAL CONFIDENCE & ROBUSTNESS ===")
messages = [{"role": "user", "content": "Show me an image of a red sports car and tell me what make it could be."}]
res = ai_port.get_answer_from_llama(messages, mode="short")
print(f"Response:\n{res}\n")

# Check 1: No apologies
has_apology = "cannot display" in res.lower() or "text-based" in res.lower()
print(f"Apology check: {'FAIL' if has_apology else 'PASS'}")

# Check 2: IMAGE_DISPLAY present
has_image = "IMAGE_DISPLAY:" in res
print(f"Image protocol check: {'PASS' if has_image else 'FAIL'}")

# Check 3: Surround text
import re
match = re.search(r'(.+)IMAGE_DISPLAY:(https?://[^\s]+)(.*)', res, re.DOTALL)
if match:
    print("PASS: Protocol detected with surrounding text.")
    print(f"Leading text: {match.group(1)[:50]}...")
    print(f"Trailing text: {match.group(3)[:50]}...")
else:
    print("FAIL: Protocol not found or not surrounded as expected.")

import ai_port

history = [
    {"role": "user", "content": "What is the current stock price of NVIDIA and give me the latest news on why it is moving."}
]

print("Starting Multi-Tool Test...")
result = ai_port.get_answer_from_llama(history, mode="detailed")
print("\nFINAL RESULT:\n")
print(result)

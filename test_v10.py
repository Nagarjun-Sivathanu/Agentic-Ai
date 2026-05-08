import ai_port
import datetime

# Test 1: Ticker Extraction
print("=== TEST 1: TICKER EXTRACTION ===")
test_query = "What is the price of MSFT stock?"
ticker = ai_port.extract_ticker(test_query)
print(f"Query: {test_query} => Extracted: {ticker}")
assert ticker == "MSFT", f"FAIL: Extracted {ticker} instead of MSFT"
print("PASS: Ticker extraction successful")

# Test 2: Temporal Grounding
print("\n=== TEST 2: TEMPORAL GROUNDING ===")
prompt = ai_port.get_system_prompt()
today = datetime.datetime.now().strftime("%B %d, %Y")
print(f"System Prompt Date: {prompt}")
assert today in prompt, f"FAIL: {today} not found in prompt"
print("PASS: Temporal grounding active")

# Test 3: Tool Execution with Date
print("\n=== TEST 3: DATE-STAMPED RESULTS ===")
res = ai_port.execute_tool("calculate", "2024 + 1")
print(f"Result: {res}")
assert "Data as of" in res or "Source:" in res, "FAIL: Citations missing"
print("PASS: Citations active")

print("\n=== PHASE 10 VERIFIED ===")

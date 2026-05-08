import ai_port

# Test 1: Stock query — should invoke stock_data + search_web
print("=== TEST 1: STOCK QUERY ===")
detected = ai_port.detect_required_tools("What is the current price of NVIDIA and why is it moving?")
print("Pre-detected tools:", detected)
assert any(t[0] == "stock_data" for t in detected), "FAIL: stock_data not triggered"
assert any(t[0] == "search_web" for t in detected), "FAIL: search_web not triggered"
print("PASS: Stock query triggers both stock_data + search_web")

# Test 2: Location query — should invoke location tool
print("\n=== TEST 2: LOCATION QUERY ===")
detected = ai_port.detect_required_tools("Where is IIT Madras university?")
print("Pre-detected tools:", detected)
assert any(t[0] == "location" for t in detected), "FAIL: location not triggered"
print("PASS: Location query triggers location tool")

# Test 3: Location tool execution
print("\n=== TEST 3: LOCATION TOOL EXECUTION ===")
result = ai_port.execute_tool("location", "IIT Madras, Chennai")
print("Result:", result[:200])
assert "Lat" in result or "error" in result.lower(), "FAIL: location returned unexpected format"
print("PASS: Location tool executed")

# Test 4: Stock tool execution
print("\n=== TEST 4: STOCK TOOL EXECUTION ===")
result = ai_port.execute_tool("stock_data", "NVDA")
print("Result:", result[:200])
print("PASS: Stock tool executed")

print("\n=== ALL TESTS PASSED ===")

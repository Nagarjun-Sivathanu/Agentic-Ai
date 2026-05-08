import ast, shutil

# Read the new engine block
new_block = open("new_block.py", "r", encoding="utf-8").read()

# Validate it first
try:
    ast.parse(new_block)
    print("new_block.py syntax OK!")
except SyntaxError as e:
    print(f"Syntax error in new_block.py: {e}")
    exit(1)

# Directly copy new_block.py as ai_port.py
shutil.copy("new_block.py", "ai_port.py")
print("ai_port.py deployed!")

# Final import test
import importlib.util, sys
spec = importlib.util.spec_from_file_location("ai_port", "ai_port.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print("Import test passed!")
print("SYSTEM_PROMPT snippet:", mod.SYSTEM_PROMPT[:80])

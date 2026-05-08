from duckduckgo_search import DDGS
try:
    results = DDGS().text("NVIDIA stock price today", max_results=5)
    for r in results:
        print(f"TITLE: {r['title']}")
        print(f"BODY: {r['body'][:200]}...")
        print("-" * 20)
except Exception as e:
    print(f"Error: {e}")

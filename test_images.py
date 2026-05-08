from duckduckgo_search import DDGS
try:
    with DDGS() as ddgs:
        results = [r for r in ddgs.images("NVIDIA headquarters", max_results=3)]
        for r in results:
            print(f"IMAGE: {r['image']}")
except Exception as e:
    print(f"Error: {e}")

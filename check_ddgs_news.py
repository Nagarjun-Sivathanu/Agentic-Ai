from duckduckgo_search import DDGS
try:
    with DDGS() as ddgs:
        results = [r for r in ddgs.news("NVIDIA", max_results=5)]
        for r in results:
            print(f"TITLE: {r['title']}")
            print(f"DATE: {r['date']}")
            print("-" * 20)
except Exception as e:
    print(f"Error: {e}")

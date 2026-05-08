import requests

def get_wiki_img(query):
    try:
        headers = {"User-Agent": "SGBC-Research-Agent/1.0 (nagun@example.com)"}
        URL = "https://en.wikipedia.org/w/api.php"
        # Search for page first
        search_params = {
            "action": "query", "list": "search", "srsearch": query, "format": "json"
        }
        search_res = requests.get(URL, params=search_params, headers=headers).json()
        if not search_res["query"]["search"]: return "None"
        title = search_res["query"]["search"][0]["title"]
        
        # Get thumbnail
        PARAMS = {
            "action": "query", "format": "json", "prop": "pageimages",
            "titles": title, "pithumbsize": 800
        }
        res = requests.get(url=URL, params=PARAMS, headers=headers).json()
        pages = res["query"]["pages"]
        for p in pages:
            if "thumbnail" in pages[p]:
                return pages[p]["thumbnail"]["source"]
    except Exception as e:
        return f"Error: {e}"
    return "No image found"

print(f"NVIDIA: {get_wiki_img('NVIDIA')}")
print(f"Eiffel Tower: {get_wiki_img('Eiffel Tower')}")

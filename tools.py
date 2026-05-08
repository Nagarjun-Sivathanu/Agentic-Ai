tools = [
    {
        "type": "function",
        "function": {
            "name": "wiki",
            "description": "Search Wikipedia to get a comprehensive summary about a specific topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "description": "The Specific topic , person or conccept to search for on wiki",
                    },
                    
                },
                "required": ["topic"],
            },
        },
    }
]


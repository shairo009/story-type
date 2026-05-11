import requests
import json

key = "sk-LsQ51RwzWpzDhqPoum8hHcZp4twSJrXL9pKOZeKHAEC1CNlUfLvvTacBJFKgqdng"
model = "minimax-m2.5-free"

providers = [
    {"name": "MiniMax Official", "url": "https://api.minimax.io/v1/chat/completions"},
    {"name": "MiniMax China", "url": "https://api.minimaxi.com/v1/chat/completions"},
    {"name": "SiliconFlow", "url": "https://api.siliconflow.cn/v1/chat/completions"},
    {"name": "OpenRouter", "url": "https://openrouter.ai/api/v1/chat/completions"},
]

def test_provider(name, url):
    print(f"Testing {name}...")
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model if name != "OpenRouter" else "minimax/minimax-m2.5:free",
        "messages": [{"role": "user", "content": "say hi"}]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Success on {name}!")
            print(response.json()["choices"][0]["message"]["content"])
            return True
        else:
            print(f"❌ Failed on {name}: {response.text}")
    except Exception as e:
        print(f"❌ Error on {name}: {e}")
    return False

for p in providers:
    if test_provider(p["name"], p["url"]):
        break

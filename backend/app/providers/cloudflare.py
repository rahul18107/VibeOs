import httpx
from app.utils.config import CF_API_TOKEN, CF_BASE_URL

async def generate(prompt: str, system: str = "", model: str = "@cf/meta/llama-3.1-8b-instruct-fast") -> str:
    
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    messages = []

    if system:
        messages.append({
            "role": "system",
            "content": system
        })

    messages.append({
        "role": "user",
        "content": prompt
    })

    payload = {
        "messages": messages
    }

    url = f"{CF_BASE_URL}/{model}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["result"]["response"]
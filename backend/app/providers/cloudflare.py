import json
import re
import httpx
from app.utils.config import CF_API_TOKEN, CF_BASE_URL

async def generate(prompt: str, system: str = "", model: str = "@cf/meta/llama-3.1-8b-instruct-fast", max_tokens: int = 4096) -> str:
    
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
        "messages": messages,
        "max_tokens": max_tokens
    }

    url = f"{CF_BASE_URL}/{model}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        result = data["result"]["response"]
        if not isinstance(result, str):
            result = json.dumps(result)
        return result


def _strip_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = [l for l in cleaned.split("\n") if not l.startswith("```")]
        cleaned = "\n".join(lines)
    return cleaned


def _repair_json(text: str) -> str:
    """Last-resort fixes for the two malformed escapes this model emits.

    Only ever applied after json.loads has already failed, so a no-op repair
    costs nothing and a wrong repair cannot corrupt an otherwise-valid parse.
    """
    # backslash before a real line break (JS line-continuation) is illegal in JSON
    repaired = re.sub(r"\\\s*\n\s*", " ", text)
    # \' is a valid JS escape but not a valid JSON one
    repaired = repaired.replace("\\'", "'")
    return repaired


async def generate_json(prompt: str, system: str = "", attempts: int = 3, **kwargs):
    last_error = None

    for _ in range(attempts):
        response = await generate(prompt=prompt, system=system, **kwargs)
        cleaned = _strip_fences(response)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            last_error = e

        try:
            return json.loads(_repair_json(cleaned))
        except json.JSONDecodeError:
            pass

    raise last_error
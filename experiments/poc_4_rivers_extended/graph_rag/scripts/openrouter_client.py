import os
import requests
from typing import List, Dict, Any, Optional


OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterClient:
    """Minimal client for OpenRouter chat completions using requests."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set in environment")

    def chat(self,
             model: str,
             messages: List[Dict[str, str]],
             temperature: float = 0.0,
             max_tokens: Optional[int] = None,
             response_format: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if response_format is not None:
            payload["response_format"] = response_format

        resp = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def first_text(response_json: Dict[str, Any]) -> str:
        try:
            return response_json["choices"][0]["message"]["content"].strip()
        except Exception:
            return ""



import requests


class LocalLLM:
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self.model = "ggml-org/Qwen3.5-0.8B-GGUF:Q4_0"

    def ask(self, user_message, system_message=None):
        if system_message is None:
            system_message = (
                "You are CareBridge, a calm offline assistant for a person "
                "with memory impairment. "
                "Use only the information provided. "
                "Keep answers short and simple. "
                "Never invent facts."
            )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.2,
            "max_tokens": 60,
        }

        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            timeout=60,
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

import os
import httpx
from typing import List, Dict, Any

class GrokService:
    def __init__(self):
        self.api_key = os.getenv("GROK_API_KEY")
        self.base_url = "https://api.x.ai/v1"
        
    async def generate_response(self, query: str, context: List[str]) -> str:
        if not self.api_key:
            # Fallback for demo if key is missing
            print("WARNING: GROK_API_KEY not set. Returning mock response.")
            return "I couldn't access Grok (API Key missing), but here is the info I found: " + " ".join(context[:2])

        prompt = self._construct_prompt(query, context)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "grok-4-latest",
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant powered by Grok. Use the provided context to answer the user's question."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"Grok API Error: {e}")
                return "Error generating response from Grok."

    def _construct_prompt(self, query: str, context: List[str]) -> str:
        context_str = "\n".join(context)
        return f"""
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {query}
Answer:
"""

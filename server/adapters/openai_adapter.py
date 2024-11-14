import openai
from server.core import ports


class OpenAIAdapter(ports.LlmPort):
    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float) -> None:
        self._openai_client = openai.OpenAI(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

    def generate_text(self, prompt: str, retrieval_context: str) -> str:
        print(prompt)
        response = self._openai_client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system",
                 "content": f"The context is: {retrieval_context}, please respond to the following question: "},
                {"role": "user", "content": prompt},
            ],
            max_tokens=self._max_tokens,
            temperature=self._temperature,
        )
        return response.choices[0].message.content

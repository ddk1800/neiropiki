from dataclasses import dataclass

import openai
import time


@dataclass
class Response:
    text: str
    time_cons: int


class ChatGPT:
    def __init__(self, token: str):
        self.openai = openai
        self.openai.api_key = token

    def create_text(self, prompt: str, model: str = "text-davinci-003", temperature: float = 0.5) -> Response:
        start = time.time()
        response = self.openai.Completion.create(
            engine=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=600,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        try:
            to_return = response['choices'][0]['text'].strip()
        except:
            to_return = "ERROR"

        end = time.time()

        return Response(to_return, int(round(end - start)))

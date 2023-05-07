from .base import Embedding, Embedder

import openai


class OpenAIEmbedding(Embedder):
    def __init__(self, engine="text-embedding-ada-002"):
        self.engine = engine

    def embed_texts(self, texts):
        resp = openai.Embedding.create(input=texts, engine=self.engine)
        data = sorted(resp["data"], key=lambda d: d["index"])
        return [d["embedding"] for d in data]

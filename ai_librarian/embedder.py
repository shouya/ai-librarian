import openai
import numpy as np

from .base import Embedding, Embedder


class OpenAIEmbedder(Embedder):
    def __init__(self, engine="text-embedding-ada-002"):
        self.engine = engine

    def embed_texts(self, texts):
        """Embeds a list of texts using the OpenAI API."""
        resp = openai.Embedding.create(input=texts, engine=self.engine)
        data = sorted(resp["data"], key=lambda d: d["index"])
        return [np.asarray(d["embedding"]) for d in data]

    # Uncomment for debugging
    #
    # def embed_texts(self, texts):
    #     """Embeds a list of texts using the OpenAI API."""
    #     return [np.random.rand(10) for _ in texts]

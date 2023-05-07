import openai
import numpy as np

from .base import Embedding, Embedder

CHUNK_SIZE = 500


class OpenAIEmbedder(Embedder):
    def __init__(self, engine="text-embedding-ada-002"):
        self.engine = engine

    def embed_texts(self, texts):
        """Embeds a list of texts using the OpenAI API."""
        embeddings = []
        for i in range(0, len(texts), CHUNK_SIZE):
            embeddings.extend(
                self.embed_texts_chunk(texts[i : i + CHUNK_SIZE])
            )
        return embeddings

    def embed_texts_chunk(self, texts):
        resp = openai.Embedding.create(input=texts, engine=self.engine)
        data = sorted(resp["data"], key=lambda d: d["index"])
        return [np.asarray(d["embedding"]) for d in data]

    # Uncomment for debugging
    #
    # def embed_texts(self, texts):
    #     """Embeds a list of texts using the OpenAI API."""
    #     return [np.random.rand(10) for _ in texts]

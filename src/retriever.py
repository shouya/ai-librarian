import langchain

import numpy as np

from .base import Retriever, Embedding, Document


class ContextualBookRetriever(Retriever):
    """Retrieve the most relevant context for docs."""

    def __init__(self, loader, embedder, doc_store):
        """Initialize the retriever."""
        self.loader = loader
        self.doc_store = doc_store
        self.embedder = embedder

    def retrieve(self, query, k):
        """Retrieve the most relevant context for docs."""
        query_embedding = self.embedder.embed_text(query)
        relevant_docs = self.doc_store.query_by_embedding(
            query_embedding, k * 5
        )
        diversified_relevant_docs = _mmr(
            self, query_embedding, relevant_docs, k
        )

        context_extended_docs = [
            self.extend_context(query_embedding, doc)
            for doc in diversified_relevant_docs
        ]
        return context_extended_docs

    def extend_context(self, query, doc):
        """Extend the context of a document until it is no longer possible."""
        new_best_doc = self.extend_context_step(query, doc)

        if new_best_doc.id == doc.id:
            return doc

        return self.extend_context(query, new_best_doc)

    def extend_context_step(self, query, doc):
        """Extend the context of a document by one step."""
        docs = [doc]
        if doc.metadata["prev_id"]:
            prev_doc = self.doc_store.get([doc.metadata["prev_id"]])[0]
            docs.append(concat_doc(prev_doc, doc))
        if doc.metadata["next_id"]:
            next_doc = self.doc_store.get([doc.metadata["next_id"]])[0]
            docs.append(concat_doc(doc, next_doc))

        best_doc = min(
            docs,
            key=lambda doc: cosine_dist(query.embedding, doc.embedding),
        )
        return best_doc


def concat_doc(a: Document, b: Document) -> Document:
    """Concatenate two documents."""
    content = a.content + b.content
    metadata = a.metadata.copy()
    metadata["prev_id"] = a.metadata["prev_id"]
    metadata["next_id"] = b.metadata["next_id"]

    embedding = a.embedding + b.embedding
    embedding_normalized = embedding / np.linalg.norm(embedding)

    id = a.id + "+" + b.id

    return Document(
        id=id,
        content=content,
        metadata=metadata,
        embedding=embedding_normalized,
    )


def cosine_dist(a: Embedding, b: Embedding):
    """Compute cosine distance between two vectors."""
    return np.dot(a, b)


def _mmr(self, query_embedding, docs, k):
    embedding_list = [doc.embedding for doc in docs]
    selected_indices = (
        langchain.vectorstores.utils.maximal_marginal_relevance(
            query_embedding, embedding_list, 0.5, k
        )
    )
    return [docs[i] for i in selected_indices]

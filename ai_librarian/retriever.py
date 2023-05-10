import langchain
import numpy as np

from typing import List
from difflib import SequenceMatcher

from .base import Retriever, Embedding, Document, DocId


class ContextualBookRetriever(Retriever):
    """Retrieve the most relevant context for docs."""

    def __init__(self, embedder, doc_store):
        """Initialize the retriever."""
        self.doc_store = doc_store
        self.embedder = embedder

    def retrieve(self, query, k):
        """Retrieve the most relevant context for docs."""
        query_embedding = self.embedder.embed_text(query)

        relevant_docs = self.doc_store.query_by_embedding(
            query_embedding, k * 5
        )

        # diversify a little
        relevant_docs = _mmr(self, query_embedding, relevant_docs, k * 2)

        # try extend the context as needed
        relevant_docs = [
            self.extend_context(query_embedding, doc)
            for doc in relevant_docs
        ]

        # remove subdocs
        relevant_docs = remove_subdocs(relevant_docs)

        # reorder based on the length, similarity, etc.
        relevant_docs = self.reorder_docs(query_embedding, relevant_docs)

        return relevant_docs[:k]

    def reorder_docs(self, query_embedding, docs):
        """Reorder the docs based on the length, similarity, etc."""

        def dist(doc):
            return cosine_dist(query_embedding, doc.embedding)

        return sorted(docs, key=dist)

    def extend_context(self, query_embedding, doc):
        """Extend the context of a document until it is no longer possible."""
        new_best_doc = self.extend_context_step(query_embedding, doc)

        if new_best_doc.id == doc.id:
            return doc

        return self.extend_context(query_embedding, new_best_doc)

    def extend_context_step(self, query_embedding, doc):
        """Extend the context of a document by one step."""
        docs = [doc]
        if doc.metadata.get("prev_id"):
            prev_doc = self.doc_store.get([doc.metadata["prev_id"]])[0]
            docs.append(concat_doc(prev_doc, doc))
        if doc.metadata.get("next_id"):
            next_doc = self.doc_store.get([doc.metadata["next_id"]])[0]
            docs.append(concat_doc(doc, next_doc))

        best_doc = min(
            docs,
            key=lambda doc: cosine_dist(query_embedding, doc.embedding),
        )
        return best_doc


def contains(a: Document, b: Document) -> bool:
    """Check if a contains b."""
    a_merged_ids = set(a.metadata.get("merged_ids", [a.id]))
    b_merged_ids = set(b.metadata.get("merged_ids", [b.id]))

    if a_merged_ids >= b_merged_ids:
        return True

    # it can happen when sentence/paragraph contains the same text
    if b.content.replace(" ", "") in a.content.replace(" ", ""):
        return True

    return False


def remove_subdocs(docs: List[Document]) -> List[Document]:
    """Detect documents contained in other documents and remove them."""
    if len(docs) <= 1:
        return docs

    new_docs = [docs[0]]
    for doc in docs[1:]:
        if not any(contains(new_doc, doc) for new_doc in new_docs):
            new_docs.append(doc)
    return new_docs


def calc_doc_id(doc: Document) -> DocId:
    """Calculate the id of a document."""
    all_ids = doc.metadata.get("merged_ids", [doc.id])
    if len(all_ids) == 1:
        return doc.id

    a = all_ids[0]
    b = all_ids[-1]

    [level_a, chap_a, part_a] = a.split(":")
    [level_b, chap_b, part_b] = b.split(":")
    assert level_a == level_b
    level = level_a

    chap_a = chap_a.split("-")[0]
    chap_b = chap_b.split("-")[-1]

    [part_a, total_a] = part_a.split("/")
    [part_b, total_b] = part_b.split("/")
    part_a = part_a.split("-")[0]
    part_b = part_b.split("-")[-1]

    chap = f"{chap_a}-{chap_b}" if chap_a != chap_b else chap_a
    part = f"{part_a}-{part_b}/{total_a}"

    id = f"{level}:{chap}:{part}"
    return id


def concat_doc(a: Document, b: Document) -> Document:
    """Concatenate two documents."""
    content = a.content + b.content
    metadata = a.metadata.copy()
    metadata["prev_id"] = a.metadata.get("prev_id")
    metadata["next_id"] = b.metadata.get("next_id")

    a_merged_ids = a.metadata.get("merged_ids", [a.id])
    b_merged_ids = b.metadata.get("merged_ids", [b.id])

    metadata["merged_ids"] = a_merged_ids + b_merged_ids

    embedding = a.embedding + b.embedding
    embedding_normalized = embedding / np.linalg.norm(embedding)

    doc = Document(
        id="UNDEF",
        content=content,
        metadata=metadata,
        embedding=embedding_normalized,
    )

    doc.id = calc_doc_id(doc)
    return doc


def concat_docs(docs: List[Document]) -> Document:
    """Concatenate a list of documents."""
    doc = docs[0]
    for d in docs[1:]:
        doc = concat_doc(doc, d)
    return doc


def cosine_dist(a: Embedding, b: Embedding):
    """Cosine distance between two vectors. Assuming both normalized."""
    return 1 - np.dot(a, b)


def _mmr(self, query_embedding, docs, k):
    embedding_list = [doc.embedding for doc in docs]
    selected_indices = (
        langchain.vectorstores.utils.maximal_marginal_relevance(
            query_embedding, embedding_list, 0.5, k
        )
    )
    return [docs[i] for i in selected_indices]

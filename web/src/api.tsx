import { BookId, Book, HistoryEntry } from "./types";

export async function listBooks(): Promise<Book[]> {
  const resp = await fetch("/api/books");
  const json = await resp.json();
  return json.map((book) => {
    return { id: book.book_id, title: book.name } as Book;
  });
}

export async function listHistory(bookId: BookId): Promise<HistoryEntry[]> {
  if (bookId === null || bookId === undefined) {
    return [];
  }

  const resp = await fetch(`/api/books/${bookId}/history`);
  const json = await resp.json();

  return json
    .map((entry) => {
      return {
        ...entry,
        references: entry.rel_docs || [],
        id: entry.log_id,
      } as HistoryEntry;
    })
    .reverse();
}

export async function ask(
  bookId: BookId,
  question: string
): Promise<HistoryEntry | null> {
  if (bookId === null || bookId === undefined || question === "") {
    return null;
  }

  const url = `/api/books/${bookId}/ask?q=${encodeURIComponent(question)}`;
  const headers = {
    "Content-Type": "application/json",
  };
  const resp = await fetch(url, { method: "POST", headers });
  const entry = await resp.json();

  return {
    ...entry,
    references: entry.rel_docs || [],
    id: entry.log_id,
  } as HistoryEntry;
}

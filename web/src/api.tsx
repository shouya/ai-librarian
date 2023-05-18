import { BookId, Book, HistoryEntry, HistoryEntryId } from "./types";

export async function listBooks(): Promise<Book[]> {
  const resp = await fetch("/api/books");
  const json = await resp.json();
  return json.map((book: any) => {
    return { id: book.book_id, title: book.name } as Book;
  });
}

export async function uploadBook(
  { title, book }: { title: string; book: File },
): Promise<Book> {
  const formData = new FormData();
  formData.append("title", title);
  formData.append("book", book);
  
  const resp = await fetch("/api/books", {
    method: "POST",
    body: formData,
  });

  if (resp.status !== 200) {
    const error = (await resp.json()).error?.message || "Unknown error";
    throw new Error(error);
  }

  const json = await resp.json();
  return { id: json.book_id, title: json.name } as Book;
}


export async function listHistory(bookId: BookId): Promise<HistoryEntry[]> {
  if (bookId === null || bookId === undefined) {
    return [];
  }

  const resp = await fetch(`/api/books/${bookId}/history`);
  const json = await resp.json();

  return json
    .map((entry: any) => {
      return {
        ...entry,
        references: entry.rel_docs || [],
        id: entry.log_id,
      } as HistoryEntry;
    })
    .reverse();
}

export async function deleteHistory(
  bookId: BookId,
  id: HistoryEntryId
): Promise<void> {
  if (
    bookId === null ||
    bookId === undefined ||
    id === null ||
    id === undefined
  ) {
    return;
  }

  const url = `/api/books/${bookId}/history/${id}`;
  await fetch(url, { method: "DELETE" });
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

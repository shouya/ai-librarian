import React from "react";

import * as t from "./types";

interface BookListItemProps {
  book: t.Book;
  isCurrent: boolean;
  setCurrentBookId: (id: t.BookId) => void;
}

function BookListItem({
  book,
  isCurrent,
  setCurrentBookId,
}: BookListItemProps) {
  return (
    <div
      className={"book-list-item " + (isCurrent ? "current" : "")}
      onClick={() => setCurrentBookId(book.id)}
    >
      {book.title}
    </div>
  );
}

interface BookListProps {
  bookList: t.Book[];
  currentBookId: t.BookId;
  setCurrentBookId: (id: t.BookId) => void;
}

export default function BookList({
  bookList,
  currentBookId,
  setCurrentBookId,
}: BookListProps) {
  return (
    <div className="book-list">
      <h2 className="heading">Select a book</h2>
      {bookList.map((book) => (
        <BookListItem
          key={book.id}
          book={book}
          isCurrent={book.id === currentBookId}
          setCurrentBookId={setCurrentBookId}
        />
      ))}
    </div>
  );
}

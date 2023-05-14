import React from "react";

import * as t from "./types";

interface IBookListItemProps {
  book: t.Book;
  isCurrent: boolean;
  setCurrentBookId: (id: t.BookId) => void;
}

function BookListItem({
  book,
  isCurrent,
  setCurrentBookId,
}: IBookListItemProps) {
  return (
    <div
      className={"book-list-item " + (isCurrent ? "current" : "")}
      onClick={() => setCurrentBookId(book.id)}
    >
      {book.title}
    </div>
  );
}

interface IBookListProps {
  bookList: t.Book[];
  currentBookId: t.BookId;
  setCurrentBookId: (id: t.BookId) => void;
}

export default function BookList({
  bookList,
  currentBookId,
  setCurrentBookId,
}: IBookListProps) {
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

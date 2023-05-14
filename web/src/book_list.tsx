import React from "react";

function BookListItem({ book, isCurrent, setCurrentBookId }) {
  return <div
    className={"book-list-item " + (isCurrent ? "current" : "")}
    onClick={() => setCurrentBookId(book.id)}>
    {book.title}
  </div>
}

export default function BookList({ bookList, currentBookId, setCurrentBookId }) {
  return <>
    <div className="book-list">
      <h2 className="heading" >Select a book</h2>
      {
        bookList.map(book =>
          <BookListItem
            key={book.id}
            book={book}
            isCurrent={book.id === currentBookId}
            setCurrentBookId={setCurrentBookId}
          />
        )
      }
    </div>
  </>;
}

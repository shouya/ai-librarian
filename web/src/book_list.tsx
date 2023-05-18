import React, { useState } from "react";
import { toast } from "react-toastify";

import { uploadBook, deleteBook } from "./api";
import * as t from "./types";

interface BookListItemProps {
  book: t.Book;
  isCurrent: boolean;
  setCurrentBookId: (id: t.BookId) => void;
  onDeleteBook: () => void;
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
      <div className="book-title">{book.title}</div>
      <div className="delete-button" onClick={() => onDeleteBook(book.id)}>
        &times;
      </div>
    </div>
  );
}

async function onUploadBook(e: React.FormEvent<HTMLFormElement>) {
  e.preventDefault();

  const formData = new FormData(e.currentTarget);
  const title = formData.get("title");
  const book = formData.get("book");
  if (!(title && book)) {
    toast.error("Missing title or book");
    return;
  }

  try {
    await uploadBook({ title: title as string, book: book as File });
    window.location.reload();
  } catch (e) {
    toast.error(e.message);
  }
}

async function onDeleteBook(id: t.BookId) {
  if (!window.confirm("Are you sure you want to delete this book?")) {
    return;
  }

  try {
    await deleteBook(id);
    window.location.reload();
  } catch (e) {
    toast.error(e.message);
  }
}

interface UploadBookModalProps {
  setShowModal: (b: boolean) => void;
}

function UploadBookModal({ setShowModal }: UploadBookModalProps) {
  return (
    <div className="modal">
      <div className="modal-content">
        <span className="close" onClick={() => setShowModal(false)}>
          &times;
        </span>
        <h2>Upload a Book</h2>
        <form onSubmit={(e) => onUploadBook(e)}>
          <div>
            <label htmlFor="title">Title:</label>
            <input type="text" id="title" name="title" />
          </div>
          <div>
            <label htmlFor="book">Book:</label>
            <input type="file" id="book" name="book" />
          </div>
          <input type="submit" value="Submit" />
        </form>
      </div>
    </div>
  );
}

interface BookListProps {
  bookList: t.Book[] | null;
  currentBookId: t.BookId | null;
  setCurrentBookId: (id: t.BookId) => void;
}

export default function BookList({
  bookList,
  currentBookId,
  setCurrentBookId,
}: BookListProps) {
  const [showModal, setShowModal] = useState(false);
  const [deleteMode, setDeleteMode] = useState(false);

  if (!bookList) {
    return (
      <div className="book-list">
        <h2 className="heading">Select a book</h2>
        <div>{"Loading..."}</div>
      </div>
    );
  }

  return (
    <>
      {showModal && <UploadBookModal setShowModal={setShowModal} />}
      <div className="book-list">
        <h2 className="upload-heading">
          <button onClick={() => setShowModal(true)}>Upload</button>
        </h2>
        <h2 className="heading">Select a book</h2>
        {bookList.map((book) => (
          <BookListItem
            key={book.id}
            book={book}
            isCurrent={book.id === currentBookId}
            setCurrentBookId={setCurrentBookId}
            onDeleteBook={() => onDeleteBook(book.id)}
          />
        ))}
      </div>
    </>
  );
}

import React, { useState, useEffect } from "react";

import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import { listBooks } from "./api";
import { ChatWindow } from "./chat_window";
import BookList from "./book_list";

import * as t from "./types";

async function initBookList({ setBookList, setCurrentBookId }) {
  await new Promise((resolve) => setTimeout(resolve, 1000));

  const books = await listBooks();
  setBookList(books);
  setCurrentBookId(books[0]?.id);
}

export default function App() {
  const [bookList, setBookList] = useState<t.Book[] | null>(null);
  const [currentBookId, setCurrentBookId] = useState<t.BookId | null>(null);

  useEffect(() => {
    initBookList({ setBookList, setCurrentBookId });
  }, []);

  return (
    <>
      <div className="container">
        <BookList
          bookList={bookList}
          currentBookId={currentBookId}
          setCurrentBookId={setCurrentBookId}
        />
        <ChatWindow bookId={currentBookId} />
      </div>
      <ToastContainer
        autoClose={2000}
        hideProgressBar
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </>
  );
}

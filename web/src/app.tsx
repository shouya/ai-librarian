import React, { useState, useEffect } from "react";

import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import { listBooks } from "./api";
import { ChatWindow } from "./chat_window";
import BookList from "./book_list";

import * as t from "./types";

export default function App() {
  const [bookList, setBookList] = useState<t.Book[]>([]);
  const [currentBookId, setCurrentBookId] = useState<t.BookId>(null);

  useEffect(() => {
    listBooks().then((books) => {
      setCurrentBookId(books[0]?.id);
      setBookList(books);
    });
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

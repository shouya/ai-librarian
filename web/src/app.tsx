import React, { useState, useEffect } from "react";

import { listBooks } from "./api";
import { ChatWindow } from "./chat_window";
import BookList from "./book_list";

export default function App() {
  const [bookList, setBookList] = useState([]);
  const [currentBookId, setCurrentBookId] = useState(null);

  useEffect(() => {
    listBooks().then((books) => {
      setCurrentBookId(books[0]?.id);
      setBookList(books);
    });
  }, []);

  return (
    <div className="container">
      <BookList
        bookList={bookList}
        currentBookId={currentBookId}
        setCurrentBookId={setCurrentBookId}
      />
      <ChatWindow bookId={currentBookId} />
    </div>
  );
}

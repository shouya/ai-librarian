import React, { useState, useReducer, useEffect } from "react";
import { listBooks, listHistory } from "./api";
import { ChatWindow } from "./chat_window";
import { chatHistoryReducer } from "./history";
import BookList from "./book_list";

export default function App() {
  const [bookList, setBookList] = useState([]);
  const [currentBookId, setCurrentBookId] = useState(null);
  const [chatHistory, dispatchChatHistory] = useReducer(chatHistoryReducer, []);

  useEffect(() => {
    listBooks().then(books => {
      setCurrentBookId(books[0]?.id);
      setBookList(books);
    });
  }, []);

  useEffect(() => {
    listHistory(currentBookId)
      .then(history => {
        dispatchChatHistory({ type: "init", bookId: currentBookId, history });
      });
  }, [currentBookId]);


  const currentBook = bookList.find(book => book.id == currentBookId);
  const currentHistory = currentBookId && chatHistory[currentBookId] || [];

  return <div className="container">
    <BookList
      bookList={bookList}
      currentBookId={currentBookId}
      setCurrentBookId={setCurrentBookId}
    />
    <ChatWindow
      bookId={currentBookId}
      book={currentBook}
      chatHistory={currentHistory}
      dispatchChatHistory={dispatchChatHistory}
    />
  </div>;
}

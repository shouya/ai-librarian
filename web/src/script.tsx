import React, { StrictMode, useState, useReducer, useRef, useEffect } from "react";
// import { useImmer, useImmerReducer } from "use-immer";
import { createRoot } from "react-dom/client";
import { listBooks, listHistory, ask } from "./api";
import { chatHistoryReducer, ChatHistoryBacklog } from "./history";


function BookListItem({ book, isCurrent, setCurrentBookId }) {
  return <div
    className={"book-list-item " + (isCurrent ? "current" : "")}
    onClick={() => setCurrentBookId(book.id)}>
    {book.title}
  </div>
}

function BookList({ bookList, currentBookId, setCurrentBookId }) {
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

async function askQuestion(bookId, question, dispatch) {
  const answer = await ask(bookId, question);
  if (answer === null) return;

  dispatch({ ...answer, bookId, type: "add" });
}

function AskBar({ bookId, dispatchChatHistory }) {
  const input_ref = useRef(null);
  const onSubmit = (e: InputEvent) => {
    e.preventDefault();
    const question = input_ref.current.value
    input_ref.current.value = "";

    askQuestion(bookId, question, dispatchChatHistory);
  };

  return <form className="ask-bar" onSubmit={onSubmit}>
    <input type="text" ref={input_ref} />
    <button>Ask</button>
  </form>;
}

function ChatWindow({ bookId, book, chatHistory, dispatchChatHistory }) {
  return <div className="chat-window">
    <ChatHistoryBacklog chatHistory={chatHistory} />
    <AskBar bookId={bookId} dispatchChatHistory={dispatchChatHistory} />
  </div>
}

function App() {
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

const root = createRoot(document.getElementById("root"));
root.render(
  <StrictMode>
    <App />
  </StrictMode>
);

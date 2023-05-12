import React, { StrictMode, useState, useReducer, useRef, useEffect } from "react";
// import { useImmer, useImmerReducer } from "use-immer";
import { createRoot } from "react-dom/client";
import { requestToGetAnswer, initHistory } from "./data";
import { listBooks, listHistory, ask } from "./api";

function chatHistoryReducer(chatHistory, action) {
    const { bookId, question, answer, quote, references } = action;
    const history = chatHistory[bookId] || [];

    if (action.type == "add") {
        const id = crypto.randomUUID();
        const historyEntry = { question, answer, quote, references, id };
        return { ...chatHistory, [bookId]: [historyEntry, ...history] }
    } else if (action.type == "init") {
        return action.history;
    } else {
        throw new Error("Invalid action type");
    }
}

function BookListItem({ book, isCurrent, setCurrentBookId }) {
    return <div
        className={"book-list-item " + (isCurrent ? "current" : "")}
        onClick={() => setCurrentBookId(book.id)}>
        {book.title}
    </div>
}

function BookList({ bookList, currentBookId, setCurrentBookId }) {
    return <div className="book-list">
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
    </div>;
}

function Reference({ reference }) {
    return <div className="reference">
        <div className="content">{reference.content}</div>
        <div className="metadata">
            <div className="chapter">{reference.metadata.chapter_title}</div>
            <div className="ref-id">{reference.id}</div>
        </div>
    </div>;
}

function ChatHistoryEntry({ history }) {
    const [expand, setExpand] = useState(false);
    const { question, answer, quote } = history;
    return <div className="chat-history-entry">
        <div className="question">{question}</div>
        <div className="answer">{answer}</div>
        <div className="quote" onClick={() => setExpand(e => !e)} title="Click to expand">{quote}</div>
        <div className={"references " + (expand && "expanded")} >
            {history.references.map(r => <Reference key={r.id} reference={r} />)}
        </div>
    </div>;
}

function ChatHistoryBacklog({ chatHistory }) {
    console.log(chatHistory);
    return <div className="chat-history-backlog">
        {chatHistory.map(entry =>
            <ChatHistoryEntry key={entry.id} history={entry} />
        )}
    </div>;
}

function askQuestion(question, bookId, dispatch) {
    requestToGetAnswer({ question, bookId }, resp => {
        const { answer, quote, rel_docs } = resp;
        dispatch({ type: "add", bookId, question, answer, quote, references: rel_docs });
    });
}

function AskBar({ bookId, dispatchChatHistory }) {
    const input_ref = useRef(null);
    const onSubmit = (e: InputEvent) => {
        e.preventDefault();
        askQuestion(input_ref.current.value, bookId, dispatchChatHistory);
        input_ref.current.value = "";
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
        listBooks(books => {
            setCurrentBookId(books[0]?.id);
            setBookList(books);
        });
    }, []);

    useEffect(() => {
        listHistory(currentBookId, history => {
            dispatchChatHistory({ type: "init", history });
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

import React, { StrictMode, useState, useReducer, useRef, useEffect } from "react";
import { chatHistoryReducer, ChatHistoryBacklog } from "./history";

async function askQuestion(bookId, question, dispatch) {
  const answer = await ask(bookId, question);
  if (answer === null) return;

  dispatch({ ...answer, bookId, type: "add" });
}

export function AskBar({ bookId, dispatchChatHistory }) {
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

export function ChatWindow({ bookId, book, chatHistory, dispatchChatHistory }) {
  return <div className="chat-window">
    <ChatHistoryBacklog chatHistory={chatHistory} />
    <AskBar bookId={bookId} dispatchChatHistory={dispatchChatHistory} />
  </div>
}

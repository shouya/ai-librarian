import React, { useReducer, useRef, useEffect } from "react";

import { listHistory, ask } from "./api";
import { ChatHistoryBacklog } from "./history";

function chatHistoryReducer(history, action) {
  if (action.type == "add") {
    const { id, question, answer, quote, error, references } = action;
    const historyEntry = {
      id,
      question,
      answer,
      quote,
      error,
      references,
    };
    return [...history, historyEntry];
  } else if (action.type == "init") {
    return action.history;
  } else {
    throw new Error("Invalid action type");
  }
}

async function askQuestion(bookId, question, dispatch) {
  const answer = await ask(bookId, question);
  if (answer === null) return;

  dispatch({ ...answer, bookId, type: "add" });
}

export function AskBar({ bookId, dispatchChatHistory }) {
  const input_ref = useRef(null);
  const onSubmit = (e) => {
    e.preventDefault();
    const question = input_ref.current.value;
    input_ref.current.value = "";

    askQuestion(bookId, question, dispatchChatHistory);
  };

  return (
    <form className="ask-bar" onSubmit={onSubmit}>
      <input type="text" ref={input_ref} />
      <button>Ask</button>
    </form>
  );
}

export function ChatWindow({ bookId }) {
  const [chatHistory, dispatchChatHistory] = useReducer(chatHistoryReducer, []);

  useEffect(() => {
    listHistory(bookId).then((history) =>
      dispatchChatHistory({ type: "init", history })
    );
  }, [bookId]);

  return (
    <div className="chat-window">
      <ChatHistoryBacklog chatHistory={chatHistory} />
      <AskBar bookId={bookId} dispatchChatHistory={dispatchChatHistory} />
    </div>
  );
}

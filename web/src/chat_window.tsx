import React, { useReducer, useRef, useEffect } from "react";

import { listHistory, ask } from "./api";
import { ChatHistoryBacklog } from "./history";

import * as t from "./types";

type HistoryAction =
  | { type: "add"; entry: t.HistoryEntry }
  | { type: "init"; history: t.History };

function historyReducer(history: t.History, action: HistoryAction) {
  if (action.type == "add") {
    return [...history, action.entry];
  } else if (action.type == "init") {
    return action.history;
  } else {
    throw new Error("Invalid action type");
  }
}

async function askQuestion(
  bookId: t.BookId,
  question: string,
  dispatch: (action: HistoryAction) => void
) {
  const entry = await ask(bookId, question);
  if (entry === null) return;

  dispatch({ type: "add", entry: entry });
}

interface IAskBarProps {
  bookId: t.BookId;
  dispatchChatHistory: (action: HistoryAction) => void;
}

export function AskBar({ bookId, dispatchChatHistory }: IAskBarProps) {
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

interface IChatWindowProps {
  bookId: t.BookId;
}
export function ChatWindow({ bookId }: IChatWindowProps) {
  const [chatHistory, dispatchChatHistory] = useReducer(historyReducer, []);

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

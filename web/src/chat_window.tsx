import React, { useReducer, useRef, useEffect } from "react";

import { listHistory, ask } from "./api";
import { HistoryBacklog } from "./history";

import * as t from "./types";

function historyReducer(history: t.History, action: t.HistoryAction) {
  if (action.type == "add") {
    return [action.entry, ...history];
  } else if (action.type == "init") {
    return action.history;
  } else if (action.type == "delete") {
    return history.filter((entry) => entry.id !== action.id);
  } else {
    throw new Error("Invalid action type");
  }
}

async function askQuestion(
  bookId: t.BookId,
  question: string,
  dispatch: (action: t.HistoryAction) => void
) {
  const entry = await ask(bookId, question);
  if (entry === null) return;

  dispatch({ type: "add", entry: entry });
}

interface IAskBarProps {
  bookId: t.BookId;
  history: t.History;
  dispatchHistory: (action: t.HistoryAction) => void;
}

export function AskBar({ bookId, history, dispatchHistory }: IAskBarProps) {
  const input_ref = useRef<HTMLInputElement>(null);
  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const question = input_ref.current.value;
    input_ref.current.value = "";
    askQuestion(bookId, question, dispatchHistory);
  };

  const onKeyUp = (e: React.KeyboardEvent) => {
    // when press up, bring up the previous question
    if (e.key !== "ArrowUp") return;
    if (input_ref.current.value !== "") return;
    const last = history[0];
    if (last === undefined) return;

    input_ref.current.value = last.question;
  };

  return (
    <form className="ask-bar" onSubmit={onSubmit}>
      <input type="text" ref={input_ref} onKeyUp={onKeyUp} />
      <button>Ask</button>
    </form>
  );
}

interface IChatWindowProps {
  bookId: t.BookId;
}
export function ChatWindow({ bookId }: IChatWindowProps) {
  const [history, dispatchHistory] = useReducer(historyReducer, []);

  useEffect(() => {
    listHistory(bookId).then((history) =>
      dispatchHistory({ type: "init", history })
    );
  }, [bookId]);

  return (
    <div className="chat-window">
      <HistoryBacklog
        bookId={bookId}
        history={history}
        dispatchHistory={dispatchHistory}
      />
      <AskBar
        bookId={bookId}
        history={history}
        dispatchHistory={dispatchHistory}
      />
    </div>
  );
}

import React, { useReducer, useRef, useEffect } from "react";

import { listHistory, ask } from "./api";
import { HistoryBacklog } from "./history";

import * as t from "./types";

type HistoryAction =
  | { type: "add"; entry: t.HistoryEntry }
  | { type: "init"; history: t.History };

function historyReducer(history: t.History, action: HistoryAction) {
  if (action.type == "add") {
    return [action.entry, ...history];
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
  history: t.History;
  dispatchHistory: (action: HistoryAction) => void;
}

export function AskBar({ bookId, history, dispatchHistory }: IAskBarProps) {
  const input_ref = useRef<HTMLInputElement>(null);
  const onSubmit = (e: InputEvent) => {
    e.preventDefault();
    const question = input_ref.current.value;
    input_ref.current.value = "";
    askQuestion(bookId, question, dispatchHistory);
  };

  const onKeyUp = (e: KeyboardEvent) => {
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
      <HistoryBacklog history={history} />
      <AskBar
        bookId={bookId}
        history={history}
        dispatchHistory={dispatchHistory}
      />
    </div>
  );
}

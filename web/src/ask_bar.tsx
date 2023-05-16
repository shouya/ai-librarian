import React, { useRef, useState } from "react";
import { toast } from "react-toastify";

import { ask } from "./api";
import * as t from "./types";

async function askQuestion(
  bookId: t.BookId,
  question: string,
  dispatch: (action: t.HistoryAction) => void
) {
  const entry = await ask(bookId, question);
  if (entry === null) return;
  dispatch({ type: "add", entry: entry });
}

interface AskBarProps {
  bookId: t.BookId;
  history: t.History;
  dispatchHistory: (action: t.HistoryAction) => void;
}

export function AskBar({ bookId, dispatchHistory }: AskBarProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) {
      toast("Please wait for the previous question to be answered.");
      return;
    }

    const question = inputRef.current?.value;
    if (!question) return;

    inputRef.current.value = "";

    setLoading(true);
    try {
      await askQuestion(bookId, question, dispatchHistory);
    } catch (e) {
      toast.error("Failed to ask question.");
      console.error(e);
    }
    setLoading(false);
  };

  const onKeyUp = (e: React.KeyboardEvent) => {
    if (e.key !== "ArrowUp") return;
    if (inputRef.current?.value !== "") return;
    const last = history[0];
    if (!last) return;
    inputRef.current.value = last.question;
  };

  return (
    <form className="ask-bar" onSubmit={onSubmit}>
      <input type="text" ref={inputRef} onKeyUp={onKeyUp} />
      <button>{loading ? "Loading..." : "Ask"}</button>
    </form>
  );
}
